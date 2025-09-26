# Contributing to NavPro

Thank you for your interest in contributing to NavPro! 🛩️

## 🚨 Aviation Safety First

**IMPORTANT**: This software is for educational and flight planning purposes only. When contributing:
- Never promote use in actual flight operations
- Always emphasize verification with official sources
- Include appropriate safety disclaimers in new features
- Test thoroughly with various data sets

## 🤝 How to Contribute

### 1. Fork & Clone
```bash
git fork https://github.com/ffdumont/nav-profile
git clone https://github.com/yourusername/nav-profile
cd nav-profile
```

### 2. Set Up Development Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 4. Make Changes
- Follow existing code style
- Add tests for new functionality
- Update documentation
- Include safety considerations

### 5. Test Your Changes
```bash
# Test GUI
python navpro/navpro_gui.py

# Test profile correction
python profile-correction/kml_profile_corrector.py test_data/sample.kml

# Test command line interface
python navpro/navpro.py --help
```

### 6. Submit Pull Request
- Clear description of changes
- Reference any related issues
- Include screenshots for GUI changes
- Confirm all tests pass

## 📋 Areas for Contribution

### High Priority
- [ ] Additional airspace format support (other countries)
- [ ] Enhanced error handling and user feedback
- [ ] Performance optimizations for large datasets
- [ ] Internationalization (i18n) support

### Medium Priority
- [ ] Additional KML visualization features
- [ ] Export to other formats (GPX, etc.)
- [ ] Integration with other flight planning tools
- [ ] Documentation improvements

### Low Priority
- [ ] Alternative GUI frameworks
- [ ] Mobile app considerations
- [ ] Advanced analytics features

## 🐛 Bug Reports

When reporting bugs, please include:
- Operating system and version
- Python version
- Steps to reproduce
- Expected vs actual behavior
- Sample files (if applicable)
- Screenshots or error messages

## 💡 Feature Requests

For new features, please consider:
- Aviation safety implications
- Compatibility with existing workflows
- Performance impact
- Documentation needs

## 📚 Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Comment complex algorithms
- Include docstrings for functions
- Keep functions focused and small

## 🔒 Security & Safety

- Never commit sensitive flight data
- Sanitize user inputs
- Validate all external data sources
- Include appropriate error handling
- Add safety warnings for critical features

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## ❓ Questions?

Feel free to open an issue for questions or discussions!

---

**Remember: Safety first, code second! ✈️**