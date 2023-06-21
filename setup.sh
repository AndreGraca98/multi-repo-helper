case ":$PATH:" in
  *:$HOME/bin:*) ;;
  *) echo "

# Added by https://github.com/AndreGraca98/multi-repo-helper
PATH=\$HOME/bin:\$PATH" >> $HOME/.bashrc ;; # Replace with your prefered shell rc file
esac


chmod +x multi_repo_helper.py
mkdir -p ~/bin
cp multi_repo_helper.py ~/bin/multi_repo_helper
