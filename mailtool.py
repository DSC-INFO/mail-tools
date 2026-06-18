import imaplib
import email
import os
from email.utils import parsedate_to_datetime, parseaddr
import sys


def clean_filename(text, max_length=64):
    # Nettoie le texte pour en faire un nom de fichier valide
    cleaned = ''.join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in text)
    return cleaned[:max_length]


def save_emails_as_eml(server, username, password, output_folder, mailbox='INBOX', max_emails=None):
    # Connexion au serveur IMAP
    mail = imaplib.IMAP4_SSL(server)
    mail.login(username, password)
    mail.select(mailbox)

    # Recherche des emails
    status, messages = mail.search(None, 'ALL')
    if status != 'OK':
        print("Erreur lors de la recherche des emails.")
        return

    email_ids = messages[0].split()
    if max_emails:
        email_ids = email_ids[-max_emails:]

    # Création du dossier de sortie
    os.makedirs(output_folder, exist_ok=True)

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

        # Construction du nom de fichier (date + expéditeur + sujet)
        base_name = f"{email_date}_{sender_name}_{subject}"
        filename = clean_filename(base_name, 64) + ".eml"
        filepath = os.path.join(output_folder, filename)

        # Sauvegarde de l'email au format .eml
        with open(filepath, 'wb') as f:
            f.write(raw_email)

        print(f"Email sauvegardé : {filepath}")

    mail.close()
    mail.logout()

# Fonction principale
if __name__ == "__main__":
    server = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    output_folder = sys.argv[4]
    save_emails_as_eml(server, username, password, output_folder)
##, max_emails=50