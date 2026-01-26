package main

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// SmartContract provides functions for managing an AttendanceAsset
type SmartContract struct {
	contractapi.Contract
}

// AttendanceAsset describes basic details of what makes up a simple attendance record
type AttendanceAsset struct {
	ID             string  `json:"id"`
	StudentID      string  `json:"student_id"`
	Timestamp      int64   `json:"timestamp"`
	Zone           string  `json:"zone"`
	Confidence     float64 `json:"confidence"`
	Engagement     float64 `json:"engagement"`
	IsCompliant    bool    `json:"is_compliant"`
	ViolationReason string `json:"violation_reason"`
	Hash           string  `json:"hash"`
}

// InitLedger adds a base set of assets to the ledger
func (s *SmartContract) InitLedger(ctx contractapi.TransactionContextInterface) error {
	assets := []AttendanceAsset{
		{ID: "genesis_block", StudentID: "SYSTEM", Timestamp: time.Now().Unix(), Zone: "ROOT", Hash: "0000000000"},
	}

	for _, asset := range assets {
		assetJSON, err := json.Marshal(asset)
		if err != nil {
			return err
		}

		err = ctx.GetStub().PutState(asset.ID, assetJSON)
		if err != nil {
			return fmt.Errorf("failed to put to world state. %v", err)
		}
	}

	return nil
}

// RecordAttendance adds a new attendance record to the world state with given details
func (s *SmartContract) RecordAttendance(ctx contractapi.TransactionContextInterface, 
	id string, studentID string, zone string, confidence float64, engagement float64, isCompliant bool, violationReason string, hash string) error {
	
	exists, err := s.AssetExists(ctx, id)
	if err != nil {
		return err
	}
	if exists {
		return fmt.Errorf("the asset %s already exists", id)
	}

	asset := AttendanceAsset{
		ID:              id,
		StudentID:       studentID,
		Timestamp:       time.Now().Unix(),
		Zone:            zone,
		Confidence:      confidence,
		Engagement:      engagement,
		IsCompliant:     isCompliant,
		ViolationReason: violationReason,
		Hash:            hash,
	}

	assetJSON, err := json.Marshal(asset)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(id, assetJSON)
}

// VerifyRecord returns the asset stored in the world state with given id
func (s *SmartContract) VerifyRecord(ctx contractapi.TransactionContextInterface, id string) (*AttendanceAsset, error) {
	assetJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return nil, fmt.Errorf("failed to read from world state: %v", err)
	}
	if assetJSON == nil {
		return nil, fmt.Errorf("the asset %s does not exist", id)
	}

	var asset AttendanceAsset
	err = json.Unmarshal(assetJSON, &asset)
	if err != nil {
		return nil, err
	}

	return &asset, nil
}

// AssetExists returns true when asset with given ID exists in world state
func (s *SmartContract) AssetExists(ctx contractapi.TransactionContextInterface, id string) (bool, error) {
	assetJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return false, fmt.Errorf("failed to read from world state: %v", err)
	}

	return assetJSON != nil, nil
}

func main() {
	assetChaincode, err := contractapi.NewChaincode(&SmartContract{})
	if err != nil {
		fmt.Printf("Error creating asset-transfer-basic chaincode: %v", err)
		return
	}

	if err := assetChaincode.Start(); err != nil {
		fmt.Printf("Error starting asset-transfer-basic chaincode: %v", err)
	}
}
