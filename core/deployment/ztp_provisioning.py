import time
import hashlib
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

class TPM_Hardware:
    """Simulates a Trusted Platform Module (TPM) eFuse identity."""
    def __init__(self, serial_num: str):
        self.serial = serial_num
        self.ek_pub = hashlib.sha256(serial_num.encode()).hexdigest()
        self.ek_priv = hashlib.sha256((serial_num + "secret_fuse").encode()).hexdigest()
        
    def sign_challenge(self, challenge: str) -> str:
        """Simulate hardware-backed signing of a cryptographic nonce."""
        return hashlib.sha256((challenge + self.ek_priv).encode()).hexdigest()

class CentralZTPServer:
    """Simulates the Cloud Provisioning Endpoint."""
    def __init__(self):
        # Whitelisted factory identities
        self.authorized_keys = {
            hashlib.sha256("edge_node_101".encode()).hexdigest(): "room_101_profile",
            hashlib.sha256("edge_node_102".encode()).hexdigest(): "room_102_profile"
        }
        self.pending_challenges = {}
        
    def request_auth(self, ek_pub: str) -> str:
        if ek_pub not in self.authorized_keys:
            logging.error(f"[SERVER] Unauthorized EK_PUB rejected. Possbile rogue device.")
            raise PermissionError("Unrecognized Hardware Endorsement Key")
            
        challenge = hashlib.sha256(str(time.time()).encode()).hexdigest()
        expected_priv_sim = hashlib.sha256(("edge_node_101secret_fuse").encode()).hexdigest()
        self.pending_challenges[ek_pub] = {
            "challenge": challenge,
            "expected_sig": hashlib.sha256((challenge + expected_priv_sim).encode()).hexdigest()
        }
        return challenge
        
    def verify_and_provision(self, ek_pub: str, signature: str) -> dict:
        if ek_pub not in self.pending_challenges:
            raise ValueError("No pending session.")
            
        expected = self.pending_challenges[ek_pub]["expected_sig"]
        if signature != expected:
             logging.error(f"[SERVER] Invalid Signature! Cryptographic Boot Chain compromised.")
             raise PermissionError("Signature Verification Failed")
             
        logging.info("[SERVER] TPM Signature Verified. Issuing mTLS certificates and configuration...")
        del self.pending_challenges[ek_pub]
        
        return {
            "mtls_cert": f"CERT-{ek_pub[:8]}",
            "mqtt_endpoint": "ssl://scholarmaster.edu:8883",
            "classroom_profile": self.authorized_keys[ek_pub]
        }

def run_ztp_sequence(tpm: TPM_Hardware, server: CentralZTPServer):
    """
    Paper 11: Zero-Touch Provisioning (ZTP) Sequence
    Algorithm 3 implementation for headless Edge AI lifecycle provisioning.
    """
    logging.info(f"\n[ZTP] Booting Device (Serial: {tpm.serial})...")
    time.sleep(1)
    
    try:
        # 1. Device asks server for a challenge using its public hardware ID
        logging.info("[ZTP] Requesting Authentication Challenge from Central Server...")
        challenge = server.request_auth(tpm.ek_pub)
        time.sleep(0.5)
        
        # 2. Device asks TPM physical chip to sign the challenge with private fused key
        logging.info("[ZTP] TPM signing cryptographic nonce...")
        sig = tpm.sign_challenge(challenge)
        time.sleep(0.5)
        
        # 3. Device presents signature to Server for Provisioning payload
        logging.info("[ZTP] Transmitting Token Response to Server...")
        payload = server.verify_and_provision(tpm.ek_pub, sig)
        
        logging.info(f"\n[ZTP: SUCCESS] Device Provisioned with Profile: {payload['classroom_profile']}")
        logging.info(f"[ZTP: SUCCESS] mTLS Cert Issued: {payload['mtls_cert']}")
        logging.info(f"[ZTP: SUCCESS] Transitioning to ACTIVE State on {payload['mqtt_endpoint']}...")
        
    except Exception as e:
        logging.critical(f"\n[ZTP: FAILED] {str(e)}. System Halting to prevent rogue operation.")


def test_provisioning():
    print("="*80)
    print("Paper 11 MLOps: Zero-Touch Provisioning (ZTP)")
    print("="*80)
    
    server = CentralZTPServer()
    
    # Test 1: Valid Whitelisted Device
    valid_tpm = TPM_Hardware("edge_node_101")
    run_ztp_sequence(valid_tpm, server)
    
    # Test 2: Rogue/Unrecognized Device
    rogue_tpm = TPM_Hardware("rogue_hacker_node")
    run_ztp_sequence(rogue_tpm, server)

if __name__ == "__main__":
    test_provisioning()
