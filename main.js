const button = document.getElementById(‘signout_button’);
    button.onclick = () => {
        google.accounts.id.disableAutoSelect();
    }
