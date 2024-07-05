Email to DevOps Issues
Beschreibung

Dieses Repository enthält ein Skript, das automatisch E-Mails verarbeitet und entsprechende Issues in Azure DevOps erstellt. Es eignet sich ideal für Teams, die E-Mail-Anfragen automatisch in trackbare Tickets umwandeln möchten.
Voraussetzungen

Bevor Sie das Projekt einrichten, stellen Sie sicher, dass Sie die folgenden Anforderungen erfüllen:

    Python 3.6 oder höher
    Zugang zu einem E-Mail-Konto mit IMAP-Unterstützung
    Ein Azure DevOps-Konto

Einrichtung
Schritte zur Installation

    Klonen Sie das Repository:

    bash

git clone https://github.com/Muslix/email-to-devops-issues.git
cd email-to-devops-issues

Installieren Sie die erforderlichen Python-Pakete:

bash

    pip install -r requirements.txt

Konfiguration der Umgebung

    Erstellen Sie eine Datei namens .env im Hauptverzeichnis des Projekts. Diese Datei wird verwendet, um sensible Daten wie Passwörter und API-Schlüssel sicher zu speichern. Fügen Sie die folgenden Zeilen hinzu und ersetzen Sie die Werte durch Ihre tatsächlichen Konfigurationsdaten:

    makefile

    HOST=mail.yourmailserver.com
    USERNAME=your-email@example.com
    MAIL_PASSWORD=your-email-password
    MAILBOX=INBOX
    ORGANIZATION=your-devops-organization
    PROJECT=your-devops-project
    ACCESS_TOKEN=your-devops-access-token

Generierung eines Access Tokens für Azure DevOps

    Loggen Sie sich in Ihr Azure DevOps-Konto ein.
    Navigieren Sie zu Benutzer-Einstellungen > Personal Access Tokens.
    Klicken Sie auf Neues Token.
    Geben Sie Ihrem Token einen Namen und wählen Sie das Ablaufdatum.
    Setzen Sie die benötigten Berechtigungen für Ihr Token, um es Ihrem Anwendungsfall entsprechend zu konfigurieren (zumindest die Berechtigung zum Erstellen von Work Items).
    Klicken Sie auf Erstellen und kopieren Sie das Token. Stellen Sie sicher, dass Sie es an einem sicheren Ort speichern, da es nach der Erstellung nicht mehr angezeigt wird.

Verwendung

Um das Skript zu starten, navigieren Sie im Terminal oder Command Prompt zum Verzeichnis des Projekts und führen Sie folgenden Befehl aus:

bash

python main.py

Das Skript prüft kontinuierlich das angegebene E-Mail-Konto auf neue Nachrichten und erstellt bei jeder neuen E-Mail ein Issue in Azure DevOps.
Unterstützung

Für Unterstützung und Fehlerberichte eröffnen Sie bitte ein Issue im GitHub-Repository.
