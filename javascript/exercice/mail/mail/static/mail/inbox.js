document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // Send email 
  document.querySelector('#compose-form').onsubmit = send_email;

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector("#email-view").style.display = "none";
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

}

function compose_reply(email) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = email.sender;
  document.querySelector('#compose-subject').value = email.subject.startsWith('Re:') ? email.subject : `Re: ${email.subject}`;
  document.querySelector('#compose-body').value = `\n\nOn ${email.timestamp}, ${email.sender} wrote:\n${email.body}`;
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector("#email-view").style.display = "none";

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Load Sent email 
  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
        // Loop through the emails
        console.log(emails);
        emails.forEach(email => show_email(email, mailbox));
        });
}

function send_email(){
  const recipients =  document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body,
      read: false
    })
  })
  .then(response => response.json())
  .then(result => {
      console.log(result);
      localStorage.clear();
      load_mailbox('sent');
  })
 
  return false;
}

function show_email(email , mailbox){
  const user = document.querySelector('#user_mail').innerText;

  // Create a new div for the email entry
  const emailDiv = document.createElement("div");
  emailDiv.className = "email-entry"; 
  emailDiv.setAttribute("data-email-id", email.id); // Store email ID

  const sender = document.createElement("p");
  sender.className = "sender"; 
  sender.innerHTML = `From : ${email.sender}`;

  const recipients = document.createElement("p");
  recipients.className = "recipients"; 
  recipients.innerHTML = `To : ${email.recipients}`;
  
  const subject = document.createElement("p");
  subject.className = "subject"; 
  subject.innerHTML = `Object : ${email.subject}`;

  const timestamp = document.createElement("p");
  timestamp.className = "timestamp"; 
  timestamp.innerHTML = `Time : ${email.timestamp}`;

  const body = document.createElement("p");
  body.className = "body"; 
  body.innerHTML = `Body : ${email.body}`; 

  const icon_archived = document.createElement("img");
  icon_archived.className = "icon1"; 
  icon_archived.src = "/static/mail/icon/archive_icons-white.png";  
  icon_archived.alt = "archive_icons";

  const icon_read = document.createElement("img");
  icon_read.className = "icon2"; 
  icon_read.src = "/static/mail/icon/unopened.png";  
  icon_read.alt = "unopened";

  if(mailbox === "sent" && email.sender === user){
    emailDiv.append(recipients, subject, timestamp,  icon_read);
  }

  if(mailbox === "inbox" || mailbox ==="archive"){
    emailDiv.append(sender, subject, timestamp,  icon_archived, icon_read);
  }

  if(email.read) {
    emailDiv.classList.add('read');
  }

  subject.onclick = () => open_email(email.id);
  recipients.onclick = () => open_email(email.id);
  sender.onclick = () => open_email(email.id);

  icon_archived.onclick = () => archived_attribute(email);
  icon_read.onclick = () => read_attribute(email);

  document.querySelector("#emails-view").appendChild(emailDiv);
}

function open_email(email_id) {
  // Hide email list
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#email-view").style.display = "block";

  // Fetch email details
  fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
      console.log("Opened Email:", email);

      // Populate email details

      document.querySelector("#email-sender").innerHTML = `From: ${email.sender}`;
      document.querySelector("#email-recipients").innerHTML = `To: ${email.recipients}`;
      document.querySelector("#email-subject").innerHTML = `Object: ${email.subject}`;
      document.querySelector("#email-timestamp").innerHTML = `Time: ${email.timestamp}`;
      document.querySelector("#email-body").innerHTML = email.body.replace(/\n/g, '<br>');

      // Mark email as read
      if (!email.read) {
        fetch(`/emails/${email_id}`, {
          method: "PUT",
          body: JSON.stringify({ 
            read: true 
          }),
        })
      }
      document.querySelector('#reply').onclick = () => compose_reply(email);
    });
  }


function archived_attribute(email){
  console.log("archived")

  fetch(`/emails/${email.id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: !email.archived
    })
  })
  .then(response => {
    load_mailbox('inbox');
  })
}

function read_attribute(email){
  console.log("read")

  fetch(`/emails/${email.id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: !email.read
    })
  })
  .then(response => {
    load_mailbox('inbox');
  })
}

