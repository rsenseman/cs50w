document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  document.getElementById('submit-button').onclick = () => {
    send_email();
    load_mailbox('sent')
  }
}

function send_email() {
    recipients = document.querySelector('#compose-recipients').value
    subject = document.querySelector('#compose-subject').value
    body = document.querySelector('#compose-body').value

    request_body={recipients:recipients, subject:subject, body:body}

    fetch('/emails', {
        method: 'POST',
        body: JSON.stringify(request_body)
      })
      .then(response => response.json());
    //   .then(result => {
    //       // Print result
    //       console.log(result);
    //   });
      
}

function makeTableHeaders(tableNode, headers) {
    rowNode = tableNode.appendChild(document.createElement('tr'))
    headers.forEach((header) => {
        th = rowNode.appendChild(document.createElement('th'))
        th.innerHTML = header
    })
}

function makeEmailLines(tableNode, emails) {
    attrs = ["sender", "recipients", "timestamp", "subject", "body"]

    emails.forEach(email => {
        rowNode = tableNode.appendChild(document.createElement('tr'))
        
        rowNode.dataset.emailID = email['id']
        rowNode.dataset.emailIsRead = email['read']
        rowNode.dataset.emailIsArchived = email['archived']

        attrs.forEach(attr => {
            td = rowNode.appendChild(document.createElement('td'))
            attrVal = email[attr]

            if (Array.isArray(attrVal)) {
                attrVal.forEach(attrValVal => {
                    p = td.appendChild(document.createElement('p'))
                    p.innerHTML = attrValVal
                })
            } else {
                td.innerHTML = attrVal
            }
            td.classList.add("emailField")
            td.classList.add(attr)
        })
        
    });

}

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  console.log(`/emails/${mailbox}`)
  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
    // Print emails
    console.log(emails);
    emailNode = document.querySelector('#emails-view')
        
    tableNode = emailNode.appendChild(document.createElement('table'))
    tableNode.classList.add("tableNode")
    makeTableHeaders(tableNode, ["From", "To", "Sent Time", "Subject", "Body"])
    makeEmailLines(tableNode, emails)
});
}