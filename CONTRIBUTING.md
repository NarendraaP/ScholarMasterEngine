# Contributing to ScholarMasterEngine

Thank you for your interest in contributing to ScholarMasterEngine! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites
- Python 3.12 or higher
- Git
- Webcam (for testing face recognition features)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/NarendraaP/ScholarMasterEngine.git
cd ScholarMasterEngine
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables** (optional)
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize data files**
```bash
# Data files will be created automatically on first run
python utils/create_superuser.py  # Create initial admin user
```

## Running the Application

### Streamlit Dashboard
```bash
streamlit run admin_panel.py
```

### FastAPI Server
```bash
python -m uvicorn api.main:app --reload
```

### Privacy Mode Demo
```bash
python privacy_pose.py
```

## Testing

### Run all tests
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_clean_architecture_use_cases.py -v
```

### Run with coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

## Code Style

### Python Style Guide
- Follow [PEP 8](https://pep8.org/) style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use meaningful variable and function names

### Architecture Principles
- **Clean Architecture**: Keep domain logic independent of frameworks
- **SOLID Principles**: Follow single responsibility, open/closed, Liskov substitution, interface segregation, and dependency inversion
- **Dependency Injection**: Use the DI container in `di/container.py`

### Import Organization
```python
# Standard library imports
import os
import sys

# Third-party imports
import numpy as np
import pandas as pd

# Local imports
from domain.entities import Student
from application.use_cases import RegisterStudentUseCase
```

## Project Structure

```
ScholarMasterEngine/
├── domain/              # Core business logic (no dependencies)
├── application/         # Use cases and business workflows
├── infrastructure/      # External service adapters
├── di/                  # Dependency injection
├── api/                 # REST API layer
├── modules_legacy/      # Legacy modules (backward compatibility)
├── tests/              # Unit and integration tests
└── utils/              # Utility scripts
```

## Contribution Guidelines

### Branching Strategy
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes

### Pull Request Process

1. **Create a feature branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**
- Write clean, documented code
- Add tests for new features
- Update documentation as needed

3. **Test your changes**
```bash
pytest tests/
```

4. **Commit with clear messages**
```bash
git commit -m "Add: Brief description of changes"
```

Commit message prefixes:
- `Add:` - New feature
- `Fix:` - Bug fix
- `Update:` - Modify existing feature
- `Refactor:` - Code restructuring
- `Docs:` - Documentation changes
- `Test:` - Add or modify tests

5. **Push and create pull request**
```bash
git push origin feature/your-feature-name
```

### Code Review
- All pull requests require review before merging
- Address reviewer comments promptly
- Keep pull requests focused and reasonably sized

## Adding New Features

### Adding a New Use Case

1. Define domain entities in `domain/entities/`
2. Create interfaces in `domain/interfaces/`
3. Implement use case in `application/use_cases/`
4. Create infrastructure adapters in `infrastructure/`
5. Register in DI container (`di/container.py`)
6. Add tests in `tests/`

### Example: Adding Email Notification Feature

```python
# 1. domain/interfaces/i_email_service.py
from abc import ABC, abstractmethod

class IEmailService(ABC):
    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> bool:
        pass

# 2. infrastructure/email/smtp_adapter.py
from domain.interfaces import IEmailService

class SMTPAdapter(IEmailService):
    def send_email(self, to: str, subject: str, body: str) -> bool:
        # Implementation
        pass

# 3. di/container.py - Register
self.email_service = SMTPAdapter()

# 4. tests/test_email_service.py
def test_send_email():
    # Test implementation
    pass
```

## Reporting Issues

### Bug Reports
Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)
- Error messages/stack traces

### Feature Requests
Include:
- Use case description
- Proposed solution
- Alternative approaches considered
- Potential impact on existing features

## Questions?

For questions or discussions:
- Open an issue on GitHub
- Tag it with `question` label

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to ScholarMasterEngine!** 🚀
