# XLF Converter Setup Guide

This guide will help you set up and run the XLF (XLIFF) Bangla to English translator script on any computer.

## Prerequisites

### 1. Install Python 3.8+ (avoid 3.13 for better compatibility)
```bash
# Check Python version
python --version
# or
python3 --version
```

### 2. Create and activate virtual environment
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate
```

### 3. Install required packages
```bash
pip install deep-translator tqdm
```

## File Setup

### 4. Copy files to target computer
- `xlfConvater.py` (the modified version with deep-translator)
- Your input XLF file (e.g., `input.xlf`)

### 5. Verify file structure
```bash
ls -la
# Should show: xlfConvater.py, input.xlf, .venv/
```

## Running the Script

### 6. Basic usage
```bash
# With default paths (modify script for your paths)
python xlfConvater.py

# With custom input/output files
python xlfConvater.py --input "your_input.xlf" --output "your_output_English.xlf"
#MY Run code
python xlfConvater.py --input "input.xlf" --output "output_English.xlf"

# With absolute paths
python xlfConvater.py --input "/path/to/input.xlf" --output "/path/to/output_English.xlf"
```

## Complete Setup Commands (Copy-Paste Ready)

```bash
# 1. Create project directory
mkdir xlf-converter
cd xlf-converter

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows

# 4. Install dependencies
pip install deep-translator tqdm

# 5. Copy your files here (xlfConvater.py and input.xlf)

# 6. Run the script
python xlfConvater.py --input "input.xlf" --output "output_English.xlf"
```

## Script Features

- **Translation**: Converts Bangla text in XLIFF files to English
- **Progress Tracking**: Shows real-time progress with colored progress bar
- **Error Handling**: Retries failed translations up to 3 times
- **Reporting**: Shows count of failed translations at the end
- **Namespace Support**: Handles XLIFF 1.2 format properly

## Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--input` | Path to input XLF file | `/var/www/html/GTrn/xlf-conv-bn-en/input.xlf` |
| `--output` | Path to output XLF file | `/var/www/html/GTrn/xlf-conv-bn-en/output_English.xlf` |

## Expected Output

```
Found 27 <trans-unit> elements in input.xlf
[Progress Bar] ██████████ 27/27 [00:20<00:00]
Completed
Failed: 0
Translated XLF file saved as output_English.xlf
```

## Troubleshooting

### If you encounter dependency issues:
```bash
# Check if packages are installed
pip list | grep -E "(deep-translator|tqdm)"

# Reinstall if needed
pip uninstall deep-translator tqdm -y
pip install deep-translator tqdm
```

### If you encounter file permission issues:
```bash
# Check file permissions
ls -la *.xlf

# Make files readable (Linux/Mac)
chmod 644 *.xlf
```

### If you encounter Python path issues:
```bash
# Use full path to Python
/usr/bin/python3 xlfConvater.py --input "input.xlf" --output "output_English.xlf"

# Or ensure virtual environment is activated
which python  # Should show .venv path
```

### For debugging:
```bash
# Run with verbose output
python -v xlfConvater.py --input "input.xlf" --output "output_English.xlf"
```

## Notes

- Internet connection required for Google Translate API
- Translation may take time depending on file size
- The script creates `<target>` tags only if they don't exist
- Existing translations are preserved
- Failed translations are reported but don't stop the process

## Dependencies Used

- **deep-translator**: Modern translation library compatible with Python 3.13
- **tqdm**: Progress bar library
- **xml.etree.ElementTree**: Built-in XML parsing
- **requests**: HTTP client (installed with deep-translator)

## File Structure After Setup

```
xlf-converter/
├── .venv/              # Virtual environment
├── xlfConvater.py      # Main script
├── input.xlf           # Your input file
└── output_English.xlf  # Generated output
```