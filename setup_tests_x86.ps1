# Setup for venv python x86
echo "Creating virtual environment"
py -3-32 -m venv test_imports_x86

# Install mangadex-downloader
echo "Installing mangadex-downloader"
& ".\test_imports_x86\Scripts\python.exe" setup.py build
Move-Item -Path ".\build\lib\mangadex_downloader" -Destination ".\test_imports_x86"
Copy-Item -Path ".\test_imports.py" -Destination ".\test_imports_x86"

# Preparing
$venvbindir_x86 = ".\Scripts"
$pythonvenv_x86 = "${venvbindir_x86}\python.exe"
$pipvenv_x86 = "${venvbindir_x86}\pip.exe"
Copy-Item -Path ".\requirements-optional.txt" -Destination ".\test_imports_x86"
Copy-Item -Path ".\requirements.txt" -Destination ".\test_imports_x86"
cd "test_imports_x86"

# Install required libraries in venv x86
echo "Installing required libraries"
& "${pipvenv_x86}" install -U wheel
& "${pipvenv_x86}" install -U -r requirements-optional.txt
& "${pipvenv_x86}" install -U -r requirements.txt

# Execute test imports
echo "Executing test imports"
& "${pythonvenv_x86}" "test_imports.py"