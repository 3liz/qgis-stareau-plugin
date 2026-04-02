#
# Run this script whenever you customize the plugin
# to your needs
#
python3 -m qgis > /dev/null && {
    # Install uv
    which uv >/dev/null || { 
        echo "Installing uv";
        curl -LsSf https://astral.sh/uv/install.sh | sh; 
    }
    echo "Qgis seems to be installed, creating venv locally with system packages"
    uv venv --system-site-packages
    echo "Updating dependencies"
    make sync
} || {
    echo "Qgis is not installed 

}

echo "Done..."
