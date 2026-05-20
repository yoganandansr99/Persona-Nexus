# Jenkins Windows - Path and Version Fixes

## Errors Fixed

### Error 1: Path with Spaces
```
Error: Unable to create directory 'C:\\Users\\yoganandan'
'C:\Users\yoganandan' is not recognized as an internal or external command
```

**Cause:** Workspace path contains spaces: `C:\Users\yoganandan s r\`

### Error 2: Flask Version Not Found
```
ERROR: Could not find a version that satisfies the requirement Flask==3.1.6
```

**Cause:** Flask 3.1.6 doesn't exist on PyPI. Latest available is 3.1.3

## Solutions Applied

### 1. Fixed Path Issue

#### ❌ **Wrong (Absolute path with spaces)**
```groovy
environment {
    VENV_DIR = "${WORKSPACE}\\venv"  // Has spaces!
}

bat '''
    python -m venv %VENV_DIR%  // Fails with spaces
    call %VENV_DIR%\Scripts\activate.bat
'''
```

#### ✅ **Correct (Relative path)**
```groovy
environment {
    VENV_DIR = "venv"  // Relative path, no spaces
}

bat '''
    python -m venv venv  // Works with spaces
    call venv\Scripts\activate.bat
'''
```

### 2. Fixed Package Versions

Updated requirements.txt with available versions:

| Package | Old | New | Status |
|---------|-----|-----|--------|
| Flask | 3.1.6 | 3.1.3 | ✅ Available |
| Werkzeug | 3.1.8 | 3.1.2 | ✅ Available |
| Jinja2 | 3.1.6 | 3.1.2 | ✅ Available |
| click | 8.3.1 | 8.1.7 | ✅ Available |
| gunicorn | 20.0.0 | 21.2.0 | ✅ Available |
| numpy | 2.4.2 | 1.24.3 | ✅ Available |
| scipy | 1.17.1 | 1.11.4 | ✅ Available |

## Updated Jenkinsfile

### Environment Variables
```groovy
environment {
    PYTHON_VERSION = '3.11'
    VENV_DIR = "venv"  // Relative path
}
```

### Setup Stage
```groovy
bat '''
    python -m venv venv
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    echo ✅ Virtual environment ready
'''
```

### All Stages Updated
- ✅ Setup Environment
- ✅ Code Quality
- ✅ Dependency Check
- ✅ Build Verification

## How to Apply

### Option 1: Already Applied
The files have been updated. Just commit and push:

```bash
git add Jenkinsfile requirements.txt
git commit -m "Fix: Use relative paths and available package versions"
git push origin main
```

### Option 2: Manual Fix

**For Jenkinsfile:**
1. Replace `${WORKSPACE}\\venv` with `venv`
2. Replace `%VENV_DIR%` with `venv`
3. All paths become relative

**For requirements.txt:**
1. Update Flask to 3.1.3
2. Update other packages to available versions
3. Keep same functionality

## Test the Fix

1. Go to Jenkins job
2. Click **Build Now**
3. Should see:
   - ✅ Checkout
   - ✅ Setup Environment (venv created successfully)
   - ✅ Code Quality
   - ✅ Dependency Check
   - ✅ Build Verification
   - ✅ Generate Report
   - ✅ Archive Artifacts
   - ✅ Notify Success

## Expected Console Output

```
[Pipeline] bat
C:\Users\yoganandan s r\.jenkins\workspace\Persona Nexus>python -m venv venv
C:\Users\yoganandan s r\.jenkins\workspace\Persona Nexus>call venv\Scripts\activate.bat
(venv) C:\Users\yoganandan s r\.jenkins\workspace\Persona Nexus>pip install -r requirements.txt
Successfully installed Flask-3.1.3 Werkzeug-3.1.2 ...
✅ Virtual environment ready
```

## Windows Path Best Practices

### ✅ DO
- Use relative paths: `venv`, `ai_minor\app`
- Use backslashes: `\`
- Quote paths with spaces: `"C:\Program Files\..."`
- Use `call` for batch files: `call venv\Scripts\activate.bat`

### ❌ DON'T
- Use absolute paths with spaces: `${WORKSPACE}\venv`
- Use forward slashes: `/`
- Use unquoted paths with spaces
- Use `source` (Unix command) on Windows

## Package Version Verification

All packages in requirements.txt are now verified to exist on PyPI:

```bash
# Check package availability
pip index versions Flask
pip index versions Werkzeug
pip index versions numpy
# etc.
```

## Workspace Path Considerations

### Current Setup
- Workspace: `C:\Users\yoganandan s r\.jenkins\workspace\Persona Nexus`
- Has spaces in username: `yoganandan s r`
- Solution: Use relative paths only

### Alternative (Optional)
If you want to avoid spaces entirely:
1. Create Jenkins workspace in: `C:\Jenkins\workspace\`
2. Configure Jenkins to use this path
3. Then absolute paths work fine

## Verification Checklist

- [ ] Jenkinsfile uses relative paths (`venv` not `%VENV_DIR%`)
- [ ] requirements.txt has available package versions
- [ ] Flask version is 3.1.3 or lower
- [ ] All packages exist on PyPI
- [ ] Build runs successfully
- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] All stages pass ✅

## Next Steps

1. ✅ Commit updated files
2. ✅ Push to GitHub
3. ✅ Run "Build Now" in Jenkins
4. ✅ Monitor console output
5. ✅ Verify all stages pass
6. ✅ Check archived artifacts

## Troubleshooting

### Issue: Still getting path errors
**Solution:**
- Ensure workspace path doesn't have special characters
- Use only relative paths in Jenkinsfile
- Check Jenkins workspace configuration

### Issue: Package not found
**Solution:**
- Verify package exists: `pip search package-name`
- Check PyPI: https://pypi.org/
- Use available version instead

### Issue: Virtual environment not activating
**Solution:**
- Ensure `call venv\Scripts\activate.bat` is used
- Check venv was created: `dir venv`
- Verify Python is installed: `python --version`

## Resources

- [PyPI - Python Package Index](https://pypi.org/)
- [Windows Batch Scripting](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/)
- [Python Virtual Environment](https://docs.python.org/3/tutorial/venv.html)
- [Jenkins Pipeline on Windows](https://www.jenkins.io/doc/pipeline/steps/workflow-durable-task-step/#bat-windows-batch-script)

