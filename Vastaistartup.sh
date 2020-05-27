apt-get update
apt-get install libglib2.0-0
apt-get install -y libsm6 libxext6 libxrender-dev
pip install opencv-python

#SSH config file to run vast ai with vscode
Host vast_ai_instance
    HostName ssh4.vast.ai
    User root
    PORT 17138
    LOCALForward 8080 localhost:8080
    IdentityFile C:\Users\sanchit\OneDrive\Documents\gen.pem
