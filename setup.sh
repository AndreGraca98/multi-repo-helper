echo "Make sure you have the following line in "
echo "your terminal initialization file (e.g. .bashrc) :"
echo "################################"
echo
echo "mkdir -p ~/bin"
echo "[ -d \"$HOME/bin\" ] && export PATH=\$PATH:\$HOME/bin"
echo
echo "################################"

# replace with your preferred shell
SHELLRC=~/.bashrc

chmod +x multi_repo_helper.py
mkdir -p ~/bin
cp multi_repo_helper.py ~/bin/mrh
. $SHELLRC

# add auto completion
if ! grep -q "# Do not edit the following line; it is used by multi_repo_helper" $SHELLRC; then
    cat multi_repo_helper_auto_complete.sh >>$SHELLRC
fi
