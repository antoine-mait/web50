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
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
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
      body: body
    })
  })
  .then(response => response.json())
  .then(result => {
      console.log(result);
  })
  localStorage.clear();
  load_mailbox('sent');
  return false;
}

function show_email(email , mailbox){
  const user = document.querySelector('#user_mail').innerText;
  console.log("Logged-in user:", user);

  // Create a new div for the email entry
  const emailDiv = document.createElement("div");
  emailDiv.className = "email-entry"; 

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


  if(mailbox === "sent" && email.sender === user){
    emailDiv.append(recipients, subject, timestamp);
  }

  if(mailbox === "inbox"){
    emailDiv.append(sender, subject, timestamp);
  }

  document.querySelector("#emails-view").appendChild(emailDiv);
  // Open specific email 
  emailDiv.onclick = () => open_email(email.id);

}

function open_email(email_id) {
  // Hide email list
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#email-view").style.display = "block";

  fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
      console.log("Opened Email:", email);

      // Populate email details
      document.querySelector("#email-sender").innerHTML = `From: ${email.sender}`;
      document.querySelector("#email-recipients").innerHTML = `To: ${email.recipients}`;
      document.querySelector("#email-subject").innerHTML = `Object: ${email.subject}`;
      document.querySelector("#email-timestamp").innerHTML = `Time: ${email.timestamp}`;
      document.querySelector("#email-body").innerHTML = email.body;
    });
}