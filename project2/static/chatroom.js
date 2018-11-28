document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('add-channel-button').onclick = add_channel;
    document.getElementById('submit-new-button').onclick = submit_message;

    // handle persisting user input in submit field. storage of user_input
    //     will be cleared in submit_message
    // on document load, retrieve last value from local storage
    if (localStorage.getItem('user_input')) {
        document.getElementById('user-input-field').value = localStorage.getItem('user_input');
    }
    // on key up, save value to local storage
    document.getElementById('user-input-field').onkeyup = function() {
        localStorage.setItem('user_input', this.value);
    }

});

function add_channel() {
    this.setAttribute("form", "new-channel-form");
    this.onclick=null;

    ul = document.getElementById("channel-list-items");
    li = document.createElement("li");

    form = document.createElement("FORM");
    form.setAttribute('id', 'new-channel-form')
    form.onsubmit = finalize_channel;

    input = document.createElement("INPUT");
    input.setAttribute("id", "new-channel-input");
    input.setAttribute("type", "text");
    input.setAttribute("autofocus", "");
    input.setAttribute("placeholder", "New Channel Name");

    form.appendChild(input);
    li.appendChild(form);
    ul.appendChild(li);
    return false;
}

function finalize_channel() {
    console.log(this.firstElementChild.value);
    link = document.createElement("A");
    link.setAttribute("href", `/${this.firstElementChild.value}`)
    link.innerHTML = this.firstElementChild.value;

    li = this.parentElement
    li.innerHTML = '';
    li.appendChild(link);

    button = document.getElementById('add-channel-button');
    button.removeAttribute("form");
    button.onclick = add_channel;
    return false;
}

function submit_message() {
    container = document.getElementById("channel-content");
    new_text = document.createElement("div");

    date_string = new Date().toLocaleTimeString();
    time_string = document.createElement("span");
    time_string.appendChild(document.createTextNode(`${date_string} `));

    preface = document.createElement("span");
    preface.appendChild(document.createTextNode(`${username}: `));

    input = document.getElementById("user-input-field");
    new_content = document.createElement("span");
    new_content.appendChild(document.createTextNode(`${input.value}`));

    new_text.appendChild(time_string);
    new_text.appendChild(preface);
    new_text.appendChild(new_content);
    container.appendChild(new_text);

    localStorage.setItem('user_input', '')
    input.value = '';
    return false;
}
