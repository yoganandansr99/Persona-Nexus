# Jenkins on Windows - Fixed Jenkinsfile

## Error Fixed

```
Cannot run program "sh" (in directory "C:\Users\yoganandan s r\.jenkins\workspace\Persona Nexus"): 
CreateProcess error=2, The system cannot find the file specified
```

## Root Cause

The Jenkinsfile was using `sh` (Unix/Linux shell) commands, but Jenkins is running on **Windows**. Windows doesn't have `sh` - it uses `cmd.exe` (batch commands).

## Solution

Changed all `sh` steps to `bat` (batch) commands for Windows compatibility.

### ❌ **Wrong (Unix/Linux)**
```groovy
sh '''
    python3 -m venv ${VENV_DIR}
    . ${VENV_DIR}/bin/activate
    pip install -r requirements.txt
'''
```

### ✅ **Correct (Windows)**
```groovy
bat '''
    python -m venv %VENV_DIR%
    call %VENV_DIR%\Scripts\activate.bat
    pip install -r requirements.txt
'''
```

## Key Changes for Windows

| Unix/Linux | Windows |
|-----------|---------|
| `sh` | `bat` |
| `${VAR}` | `%VAR%` |
| `/path/to/file` | `\path\to\file` |
| `. venv/bin/activate` | `call venv\Scripts\activate.bat` |
| `python3` | `python` |
| `#` (comment) | `REM` (comment) |
| `mkdir dir` | `mkdir dir` |
| `cp file1 file2` | `copy file1 file2` |
| `rm -rf dir` | `rmdir /s /q dir` |

## Updated Jenkinsfile Structure

```groovy
pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.11'
        VENV_DIR = "${WORKSPACE}\\venv"  // Windows path
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_MSG = bat(script: '@git log -1 --pretty=%%B', returnStdout: true).trim()
                }
            }
        }
        
        stage('Setup Environment') {
            steps {
                bat '''
                    python -m venv %VENV_DIR%
                    call %VENV_DIR%\Scripts\activate.bat
                    pip install -r requirements.txt
                '''
            }
        }
        
        // ... more stages using bat instead of sh
    }
}
```

## Windows-Specific Commands

### Activate Virtual Environment
```batch
call %VENV_DIR%\Scripts\activate.bat
```

### Run Python
```batch
python -c "from app import app; print('OK')"
```

### Create Directory
```batch
if not exist build_artifacts mkdir build_artifacts
```

### Copy Files
```batch
copy requirements.txt build_artifacts\
xcopy ai_minor\app build_artifacts\app /E /I /Y
```

### List Files
```batch
dir
```

### Remove Directory
```batch
rmdir /s /q %VENV_DIR%
```

## How to Apply

### Option 1: Already Applied
The Jenkinsfile has been updated for Windows. Just commit and push:

```bash
git add Jenkinsfile
git commit -m "Fix: Use bat commands for Windows Jenkins"
git push origin main
```

### Option 2: Manual Fix
If you want to fix it yourself:
1. Replace all `sh '''` with `bat '''`
2. Replace all `${VAR}` with `%VAR%`
3. Replace all `/` with `\` in paths
4. Replace `. venv/bin/activate` with `call venv\Scripts\activate.bat`
5. Replace `python3` with `python`
6. Replace `#` comments with `REM`

## Test the Fix

1. Go to Jenkins job
2. Click **Build Now**
3. Should see all stages pass:
   - ✅ Checkout
   - ✅ Setup Environment
   - ✅ Code Quality
   - ✅ Dependency Check
   - ✅ Build Verification
   - ✅ Generate Report
   - ✅ Archive Artifacts
   - ✅ Notify Success
   - ✅ Cleanup (post)

## Expected Console Output

```
[Pipeline] stage
[Pipeline] { (Setup Environment)
[Pipeline] bat
[WS-CLEANUP] Deleting project workspace...
C:\Users\yoganandan s r\.jenkins\workspace\Persona Nexus>python -m venv C:\Users\yoganandan s r\.jenkins\workspace\Persona Nexus\venv
C:\Users\yoganandan s r\.jenkins\workspace\Persona Nexus>call C:\Users\yoganandan s r\.jenkins\workspace\Persona Nexus\venv\Scripts\activate.bat
(venv) C:\Users\yoganandan s r\.jenkins\workspace\Persona Nexus>pip install -r requirements.txt
Successfully installed ...
✅ Virtual environment ready
[Pipeline] }
[Pipeline] // stage
```

## Windows Path Handling

### Environment Variables
```groovy
environment {
    VENV_DIR = "${WORKSPACE}\\venv"  // Double backslash
    PYTHON_PATH = "${WORKSPACE}\\venv\\Scripts\\python.exe"
}
```

### In bat Commands
```batch
call %VENV_DIR%\Scripts\activate.bat  // Single backslash
python %PYTHON_PATH% script.py
```

## Common Windows Jenkins Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `Cannot run program "sh"` | Using Unix commands | Use `bat` instead of `sh` |
| `The system cannot find the file` | Wrong path format | Use backslashes `\` not forward slashes `/` |
| `'python' is not recognized` | Python not in PATH | Install Python and add to PATH |
| `Permission denied` | File permissions | Run Jenkins as Administrator |
| `Path too long` | Windows path limit | Use shorter workspace path |

## Verification Checklist

- [ ] Jenkinsfile uses `bat` instead of `sh`
- [ ] Environment variables use `%VAR%` format
- [ ] Paths use backslashes `\`
- [ ] Virtual environment activation uses `call ... activate.bat`
- [ ] Python command is `python` not `python3`
- [ ] Comments use `REM` not `#`
- [ ] Build runs successfully
- [ ] All stages show ✅

## Next Steps

1. ✅ Commit updated Jenkinsfile
2. ✅ Push to GitHub
3. ✅ Run "Build Now" in Jenkins
4. ✅ Monitor console output
5. ✅ Verify all stages pass
6. ✅ Check archived artifacts

## Windows Jenkins Best Practices

1. **Use `bat` for Windows commands**
   - `bat` runs batch/cmd commands
   - `sh` runs Unix/Linux shell commands

2. **Use correct path separators**
   - Windows: `\` (backslash)
   - Unix/Linux: `/` (forward slash)

3. **Use correct variable format**
   - Windows: `%VAR%`
   - Unix/Linux: `$VAR` or `${VAR}`

4. **Activate virtual environment properly**
   - Windows: `call venv\Scripts\activate.bat`
   - Unix/Linux: `. venv/bin/activate`

5. **Use correct Python command**
   - Windows: `python` (usually)
   - Unix/Linux: `python3` (usually)

## Resources

- [Jenkins Pipeline Steps - bat](https://www.jenkins.io/doc/pipeline/steps/workflow-durable-task-step/#bat-windows-batch-script)
- [Windows Batch Commands](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands-ref)
- [Python Virtual Environment on Windows](https://docs.python.org/3/tutorial/venv.html)

## Support

If you still get errors:
1. Check Jenkins console output
2. Verify Python is installed: `python --version`
3. Verify Git is installed: `git --version`
4. Check workspace path doesn't have spaces (or use quotes)
5. Run Jenkins as Administrator if permission issues

