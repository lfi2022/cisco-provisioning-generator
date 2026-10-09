# LFINFO Cisco Provisioning Generator

Interface web locale pour générer les fichiers `SEP<MAC>.cnf.xml` des Cisco 78xx Enterprise utilisés avec Asterisk / FreePBX.

## Objectif

Le projet est volontairement séparé de FreePBX :

- FreePBX/Asterisk : SIP, RTP, routage.
- LXC provisioning : interface web, génération XML, TFTP, fichiers annexes.
- Téléphones : provisioning vers le LXC, SIP vers FreePBX.

Le générateur expose un grand nombre d'options Enterprise connues et laisse également un champ **XML personnalisé** afin de ne pas bloquer les paramètres non encore modélisés.

> Important : Cisco ne publie pas un schéma public exhaustif de toutes les balises Enterprise supportées par chaque release. Certaines options proposées sont donc marquées `expérimental`. Le générateur n'affirme pas qu'elles sont toutes acceptées par le firmware 14.2.1.

## Installation recommandée sur Debian 13 LXC

```bash
apt update
apt install -y python3 python3-venv tftpd-hpa nginx
mkdir -p /opt/lfinfo-provisioning
cp -a . /opt/lfinfo-provisioning/
cd /opt/lfinfo-provisioning

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

mkdir -p /srv/provisioning/tftp
mkdir -p /var/lib/cisco-provisioning
chown -R www-data:www-data /srv/provisioning /var/lib/cisco-provisioning
```

Éditer `/etc/default/tftpd-hpa` :

```ini
TFTP_USERNAME="tftp"
TFTP_DIRECTORY="/srv/provisioning/tftp"
TFTP_ADDRESS=":69"
TFTP_OPTIONS="--secure"
```

Puis :

```bash
systemctl restart tftpd-hpa
cp systemd/lfinfo-provisioning.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now lfinfo-provisioning
```

Interface :

```text
http://IP_DU_LXC:8080
```

Vérification après installation ou mise à jour :

```bash
cd /opt/lfinfo-provisioning
.venv/bin/python -m unittest discover -s tests -v
systemctl restart lfinfo-provisioning
systemctl status lfinfo-provisioning --no-pager
```

## Fichiers générés

Pour une MAC `70:1F:53:4D:19:C8` :

```text
/srv/provisioning/tftp/SEP701F534D19C8.cnf.xml
```

Le générateur crée aussi `dialplan.xml` à la demande.

## Remarques Cisco 7841 Enterprise

Le firmware Enterprise peut afficher jusqu'à 4 touches de ligne/fonction, mais l'utilisation de plusieurs comptes SIP indépendants avec Asterisk peut provoquer un mélange des identifiants d'authentification sur certains firmwares. Le profil par défaut utilise donc une seule vraie ligne SIP et des BLF / speed-dials pour les autres touches.

Les options peuvent être passées en mode expert pour tester d'autres combinaisons.

## Limites et sécurité

- Une seule ligne SIP enregistrée par téléphone est la configuration recommandée
  pour les 78xx Enterprise avec Asterisk. Des lignes SIP supplémentaires restent
  disponibles à titre expérimental ; le générateur ne les présente pas comme
  fiables.
- Les valeurs de formulaire sont échappées pour préserver un XML valide. La zone
  **XML personnalisé** est volontairement la seule zone d'injection XML brut :
  elle est réservée à un administrateur de confiance.
- Les fichiers TFTP sont écrits de façon atomique, afin qu'un téléphone ne lise
  pas un fichier partiellement généré.
