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
COMPLETE_FILE=~/.bash_completion

chmod +x multi_repo_helper.py
mkdir -p ~/bin
cp multi_repo_helper.py ~/bin/mrh
. $SHELLRC

[ -r $COMPLETE_FILE ] || echo $COMPLETE_FILE does not exist. Creating... && touch $COMPLETE_FILE

# add auto completion to COMPLETE_FILE
if ! grep -q "# Do not edit the following line; it is used by multi_repo_helper" $COMPLETE_FILE; then
    echo "Adding auto completion to $COMPLETE_FILE"
    cat multi_repo_helper_auto_complete.sh >>$COMPLETE_FILE
fi

HOME_PATERN=$(echo $HOME | sed 's/\//\\\//g;s/\./\\./g')
RAW_COMPLETE_FILE=$(echo $COMPLETE_FILE | sed "s/$HOME_PATERN/~/g")

# add source to SHELLRC
if ! grep -q "[ -r $RAW_COMPLETE_FILE ] && source $RAW_COMPLETE_FILE" $SHELLRC; then
    echo "Adding source to $SHELLRC"
    echo -e "\n# Auto completion for multi_repo_helper\n[ -r $RAW_COMPLETE_FILE ] && source $RAW_COMPLETE_FILE" >>$SHELLRC
fi
