# Setup for venv python x64
echo "Creating virtual environment"
py -3-64 -m venv test_imports_x64

# Install mangadex-downloader
echo "Installing mangadex-downloader"
& ".\test_imports_x64\Scripts\python.exe" setup.py build
Move-Item -Path ".\build\lib\mangadex_downloader" -Destination ".\test_imports_x64"
Copy-Item -Path ".\test_imports.py" -Destination ".\test_imports_x64"

# Preparing
$venvbindir_x64 = ".\Scripts"
$pythonvenv_x64 = "${venvbindir_x64}\python.exe"
$pipvenv_x64 = "${venvbindir_x64}\pip.exe"
Copy-Item -Path ".\requirements-optional.txt" -Destination ".\test_imports_x64"
Copy-Item -Path ".\requirements.txt" -Destination ".\test_imports_x64"
cd "test_imports_x64"

# Install required libraries in venv x64
echo "Installing required libraries"
& "${pipvenv_x64}" install -U wheel
& "${pipvenv_x64}" install -U -r requirements-optional.txt
& "${pipvenv_x64}" install -U -r requirements.txt

# Execute test imports
echo "Executing test imports"
& "${pythonvenv_x64}" "test_imports.py"