#!/bin/bash

# Script to generate SSL certificates for curator.abbanoa.aigensolutions.it
# For production, use Let's Encrypt or proper certificates

DOMAIN="curator.abbanoa.aigensolutions.it"
SSL_DIR="/root/abbanoa-water-analysis/nginx/ssl"

# Create SSL directory if it doesn't exist
mkdir -p "$SSL_DIR"

# Generate a private key
openssl genrsa -out "$SSL_DIR/privkey.pem" 2048

# Generate a certificate signing request
openssl req -new -key "$SSL_DIR/privkey.pem" \
    -out "$SSL_DIR/csr.pem" \
    -subj "/C=IT/ST=Sardinia/L=Cagliari/O=Abbanoa/CN=$DOMAIN"

# Generate a self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 \
    -in "$SSL_DIR/csr.pem" \
    -signkey "$SSL_DIR/privkey.pem" \
    -out "$SSL_DIR/fullchain.pem"

# Generate DH parameters for enhanced security (optional, takes time)
# openssl dhparam -out "$SSL_DIR/dhparam.pem" 2048

# Set appropriate permissions
chmod 600 "$SSL_DIR/privkey.pem"
chmod 644 "$SSL_DIR/fullchain.pem"

echo "SSL certificates generated successfully in $SSL_DIR"
echo ""
echo "Files created:"
echo "  - $SSL_DIR/privkey.pem (private key)"
echo "  - $SSL_DIR/fullchain.pem (certificate)"
echo ""
echo "Note: This is a self-signed certificate for development."
echo "For production, use Let's Encrypt or a proper CA-signed certificate."