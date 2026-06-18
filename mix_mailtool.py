import imaplib
import email
import os
import sys
from email.utils import parsedate_to_datetime, parseaddr

def dump(mail,output_folder,mailbox):
    if mailbox!='INBOX':
        list_result = mail.list()
        (command_result, list_content) = list_result
        print(command_result)
        print(list_content)
        for item in list_content:
            print(item.decode('utf-8'))
            if '\\Sent' in item.decode('utf-8'):
                mailbox = item.decode('utf-8').split(' "/" ')[1]
        mail.select(mailbox)
    else:
        mail.select(mailbox)

    # Recherche des emails
    status, messages = mail.search(None, 'ALL')
    if status != 'OK':
        print(f"Erreur: impossible de lister les emails dans la boîte '{mailbox}'.")
        mail.close()
        mail.logout()
        return

    email_ids = messages[0].split()
    if max_emails:
        email_ids = email_ids[-max_emails:]


    # Création du dossier de sortie
    os.makedirs(output_folder, exist_ok=True)
    inbox_output_folder = os.path.join(output_folder,'Inbox')
    os.makedirs(inbox_output_folder, exist_ok=True)
    sent_output_folder = os.path.join(output_folder,'Sent')
    os.makedirs(sent_output_folder, exist_ok=True)
    
    #os.makedirs('Inbox', exist_ok=True)
    #os.makedirs('Inbox', exist_ok=True)
    #os.path.join(output_folder,'Inbox')
    #os.path.join(output_folder,'Sent')

    traité = 0
    for email_id in email_ids:
        # Récupération de l'email
        status, msg_data = mail.fetch(email_id, '(RFC822)')
        if status != 'OK':
            print(f"Erreur lors de la récupération de l'email {email_id}.")
            continue

        raw_email = msg_data[0][1]
        email_message = email.message_from_bytes(raw_email)

        # Extraction des informations pour le nom de fichier
        email_date = parsedate_to_datetime(email_message['Date']).strftime('%Y-%m-%d_%H-%M-%S')
        sender_name, sender_addr = parseaddr(email_message['From'])
        sender_name = sender_name or sender_addr.split('@')[0] or "unknown"
        subject = email_message['Subject'] or "no_subject"

        # Construction du nom de fichier
        base_name = f"{email_date}_{sender_name}_{subject}"
        filename = clean_filename(base_name, 64) + ".eml"
        if mailbox == 'INBOX':
            filepath = os.path.join(inbox_output_folder, filename)
        else:
            filepath = os.path.join(sent_output_folder, filename)

        # Sauvegarde de l'email au format .eml
        if not os.path.exists(filepath):
            with open(filepath, 'wb') as f:
                f.write(raw_email)
            print(f"Email sauvegardé : {filepath}")

        traité += 1
        if traité%25 == 0:
            print(traité,"messages traités")


         
def clean_filename(text, max_length=64):
    # Nettoie le texte pour en faire un nom de fichier valide
    cleaned = ''.join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in text)
    return cleaned[:max_length]

def save_sent_emails_as_eml(server, username, password, output_folder, max_emails=None):
    """
    Sauvegarde les emails envoyés au format .eml.

    Args:
        server: Adresse du serveur IMAP (ex: imap.gmail.com)
        username: Adresse email
        password: Mot de passe ou token d'application
        output_folder: Dossier de sortie pour les fichiers .eml
        mailbox: Nom de la boîte des emails envoyés (SENT, [Gmail]/Sent Mail, Envoyés, etc.)
        max_emails: Nombre maximal d'emails à sauvegarder (None = tous)
    """
    # Connexion au serveur IMAP
    mail = imaplib.IMAP4_SSL(server)
    mail.login(username, password)

    dump(mail,output_folder,'INBOX')
    print("Inbox mails are finished")
    dump(mail,output_folder,'SENT')
    print("Sent mails are finished")


    mail.close()
    mail.logout()

# Exemple d'utilisation
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python mailtool_sent.py <server> <username> <password> <output_folder> [max_emails]")
        sys.exit(1)

    server = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    output_folder = sys.argv[4]
    max_emails = int(sys.argv[5]) if len(sys.argv) > 5 else None

    save_sent_emails_as_eml(server, username, password, output_folder, max_emails)