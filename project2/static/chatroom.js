

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('add-channel-button').onclick = add_channel;
    document.getElementById('submit-new-button').onclick = submit_message;



    channels = document.getElementsByClassName('channel-in-channel-list')
    for (channel of channels) {
        channel.href='javascript:';
        channel.onclick=show_channel;
    }

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
    url_arr = window.location.href.substring(0).split('/');
    if (url_arr.length > 4) {
        show_channel(url_arr[url_arr.length-1]);
    } else if (channel_select.length > 0) {
        show_channel(channel_select);
    } else {
        document.getElementById("channel-content").innerHTML='Welcome to the chatroom!';
    }

    // connect to socketio
    socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('new_message', data => {
        console.log('new message here')
        console.log(data)
        channel_submitted_to = data.channel_name;
        url_arr = window.location.href.substring(0).split('/');
        if ((url_arr.length > 4) && (url_arr[url_arr.length-1]===channel_submitted_to)) {
            add_new_message(data.date_string, data.username, data.message_text, data.message_id);
        }
        return false;
    });

    socket.on('new_vote', data => {
        console.log('new vote here')
        console.log(data)

        message_container = document.getElementById(data.message_id);
        console.log(message_container);
        if (message_container) {
            emoji_block = message_container.children[2];
            console.log(emoji_block)
            emoji_block.childNodes.forEach((node) => {
            console.log(node.children[0].getAttribute('class'));
                if (node.children[0].getAttribute('class') == `emoji-${data.vote}`) {
            	       node.children[1].innerHTML = (parseInt(node.children[1].innerHTML) + 1).toString();
          	    }
            });
        }

        return false;
    });

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
    const request = new XMLHttpRequest();
    const channel_name = this.firstElementChild.value;

    request.open('POST', '/add_new_channel');
    const data = new FormData();
    data.append('channel_name', channel_name);
    request.send(data);

    link = document.createElement("A");
    link.href='javascript:';
    link.onclick = show_channel;
    link.setAttribute("class", "channel-in-channel-list")
    // link.setAttribute("href", `/channel/${channel_name}`)
    link.innerHTML = channel_name;

    li = this.parentElement
    li.innerHTML = '';
    li.appendChild(link);

    button = document.getElementById('add-channel-button');
    button.removeAttribute("form");
    button.onclick = add_channel;
    return false;
}

function show_channel(channel_name) {
    // clear existing content
    // history.pushState('whatever', `${this.innerHTML}`, `/channel/${this.innerHTML}`);
    document.getElementById("channel-content").innerHTML='';
    document.getElementById("user-input-form").removeAttribute('hidden');
    // if channel_name is a click event instead of a string, replace it with the
    // link contents
    if (!(typeof channel_name === 'string' || channel_name instanceof String)) {
        channel_name = this.innerHTML;
    }
    console.log(channel_name);
    selectors = document.getElementsByClassName('channel-in-channel-list')
    for (selector of selectors) {
        if (selector.text === channel_name) {
            selector.style['fontWeight']='bold';
        } else {
            selector.style['fontWeight']='normal';
        }
    }

    const request = new XMLHttpRequest();
    request.open('POST', `/channel/${channel_name}`);
    request.onload = () => {
        const request_data = JSON.parse(request.responseText);
        const messages = Object.entries(request_data.messages);
        for (message_arr of messages) {
            console.log(message_arr);
            console.log(message_arr[1]);
            let [time, user, message, message_id, smile_count, frown_count, sad_count, shrug_count] = message_arr[1];
            add_new_message(time, user, message, message_id, [smile_count, frown_count, sad_count, shrug_count]);
        }

        if (document.getElementById("channel-content").children.length === 0) {
            add_intro();
        }

        history.replaceState(channel_name, null, `/channel/${channel_name}`);
    }
    request.send();
}

function add_intro() {
    time_string = new Date().toLocaleTimeString();
    add_new_message(
        time_string,
        'Helpful Harold',
        'When you submit text to the channel, it will show up here.'
    );
}

function add_new_message(date_string, username, message_text, message_id, emoji_votes) {
    container = document.getElementById("channel-content");
    group_container = document.createElement("div");
    group_container.setAttribute("id", `${message_id}`);

    // message text
    new_text = document.createElement("div");
    time_string = document.createElement("span");
    time_string.setAttribute("class", "time-sent");
    time_string.appendChild(document.createTextNode(`${date_string} `));

    preface = document.createElement("span");
    preface.setAttribute("class", "sender");
    preface.appendChild(document.createTextNode(`${username}: `));

    new_content = document.createElement("span");
    new_content.setAttribute("class", "message-text");
    new_content.appendChild(document.createTextNode(`${message_text}`));

    // message emoji votes
    emoji_block = document.createElement("div");

    emoji_votes = emoji_votes || [0,0,0,0];
    emoji_names = ['smile', 'frown', 'sad', 'shrug'];
    emoji_array = ['&#x1F600', '&#x1F641', '&#x1F622', '&#x1F937'];
    for (i = 0; i < emoji_array.length; i++) {
        button = document.createElement("button");
        button.setAttribute("type", "button");
        button.setAttribute("class", "emoji-button");
        button.onclick = function() {
            date = new Date();
            date_timestamp = date.getTime();

            vote = this.firstChild.getAttribute('class').split('-')[1]

            console.log({
                'message_id': message_id,
                'vote': vote,
                'timestamp': date_timestamp
            });
            socket.emit('new_vote', {
                'message_id': message_id,
                'vote': vote,
                'timestamp': date_timestamp
            });
        }

        emoji = document.createElement('span');
        emoji.setAttribute('class', `emoji-${emoji_names[i]}`);
        emoji.innerHTML = emoji_array[i];

        votes = document.createElement('span');
        votes.setAttribute('class', 'vote-count');
        votes.innerHTML = emoji_votes[i];

        button.appendChild(emoji);
        button.appendChild(votes);
        emoji_block.appendChild(button);
    }

    new_text.appendChild(time_string);
    new_text.appendChild(preface);
    new_text.appendChild(new_content);
    group_container.appendChild(new_text);
    group_container.appendChild(document.createElement('br'));
    group_container.appendChild(emoji_block);
    group_container.appendChild(document.createElement('br'));
    container.appendChild(group_container);

    return false;
}

function submit_message() {
    date = new Date();
    date_string = date.toLocaleTimeString();
    date_timestamp = date.getTime();
    input = document.getElementById("user-input-field");
    message_text = input.value;

    url_arr = window.location.href.substring(0).split('/')
    channel_name = url_arr[url_arr.length-1];

    // Send the message two places:
    // 1) send a request to flask server to store it in the database
    // 2) emit the submission to socketio

    // submit the message to the flask server to be stored
    const request = new XMLHttpRequest();
    request.open('POST', '/submit_message');

    request.onload = () => {
        const request_data = JSON.parse(request.responseText);
        uid = request_data.message_uid;

        // emit the submission
        socket.emit('new_message', {
            'channel_name': channel_name,
            'message_text': message_text,
            'date_string': date_string,
            'username': username,
            'message_id': uid
        });
    }
    const data = new FormData();
    data.append('channel_name', channel_name);
    data.append('message_text', message_text);
    data.append('timestamp', date_timestamp);

    request.send(data);

    // reset field and local storage to empty strings
    localStorage.setItem('user_input', '')
    input.value = '';
    return false;
}
