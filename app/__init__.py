"""Sikika delivery layer — USSD/SMS webhooks over the AI core.

Africa's Talking (sandbox) posts to /ussd and /sms; the state machine in
ussd.py reads AI-simplified content from the SQLite store and records votes
and feedback against a SHA-256 hash of the phone number (never the number).
"""
