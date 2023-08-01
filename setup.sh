echo "Make sure you have the following line in "
echo "your terminal initialization file (e.g. .bashrc) :"
echo "################################"
echo
echo 'if [ -d "$HOME/bin" ]'
echo 'then'
echo '    export PATH=$PATH:$HOME/bin'
echo 'fi'
echo
echo "################################"

chmod +x multi_repo_helper.py
mkdir -p ~/bin
cp multi_repo_helper.py ~/bin/mrh
# replace with your preferred way of reloading the shell
. $HOME/.bashrc

# add auto completion
. multi_repo_helper_auto_complete.sh
. $HOME/.bashrc
