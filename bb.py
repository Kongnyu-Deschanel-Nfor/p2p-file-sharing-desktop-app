#!/usr/bin/env python3

import socket
import subprocess
import platform
import re
import sys
import ipaddress

def is_valid_ip(ip_str: str) -> bool:
    """Validate if the string is a valid IP address"""
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def get_device_name(ip_address: str) -> dict:
    """
    Attempts to get human-readable device information using multiple methods
    Returns a dictionary with all available device identifiers
    """
    device_info = {
        'ip': ip_address,
        'hostname': None,
        'netbios_name': None,
        'mdns_name': None
    }
    
    print("\nGathering information...")
    
    # Method 1: Try basic DNS lookup
    try:
        print("Attempting DNS lookup...")
        device_info['hostname'] = socket.gethostbyaddr(ip_address)[0]
    except socket.herror:
        print("DNS lookup failed")
    
    # Method 2: Try NetBIOS name (Windows network)
    if platform.system() == "Windows":
        try:
            print("Attempting NetBIOS lookup...")
            result = subprocess.run(['nbtstat', '-A', ip_address], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=2)
            # Extract NetBIOS name from output
            match = re.search(r"(\S+)\s+<00>\s+UNIQUE", result.stdout)
            if match:
                device_info['netbios_name'] = match.group(1).strip()
        except:
            print("NetBIOS lookup failed")
    
    # Method 3: Try mDNS lookup
    try:
        print("Attempting mDNS lookup...")
        if platform.system() in ["Darwin", "Linux"]:  # MacOS or Linux
            result = subprocess.run(['avahi-resolve', '-a', ip_address], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=2)
            if result.stdout:
                device_info['mdns_name'] = result.stdout.split()[-1]
        else:  # Windows
            result = subprocess.run(['ping', '-a', ip_address], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=2)
            match = re.search(r"Pinging ([^\s]+)", result.stdout)
            if match:
                device_info['mdns_name'] = match.group(1)
    except:
        print("mDNS lookup failed")

    # Get the best available name
    def get_best_name():
        if device_info['netbios_name']:
            return device_info['netbios_name']
        elif device_info['mdns_name'] and '.local' in device_info['mdns_name']:
            return device_info['mdns_name'].replace('.local', '')
        elif device_info['hostname']:
            return device_info['hostname']
        return ip_address

    device_info['friendly_name'] = get_best_name()
    return device_info

def print_device_info(info: dict):
    """Print the device information in a formatted way"""
    print("\n" + "="*50)
    print(f"Device Information for {info['ip']}")
    print("="*50)
    print(f"✨ Friendly Name: {info['friendly_name']}")
    print(f"🌐 Hostname: {info['hostname'] or 'Not found'}")
    print(f"💻 NetBIOS Name: {info['netbios_name'] or 'Not found'}")
    print(f"📱 mDNS Name: {info['mdns_name'] or 'Not found'}")
    print("="*50)

def main():
    """Main function to run the device information tool"""
    print("Welcome to Device Info Finder!")
    print("This tool helps you discover information about devices on your network.")
    
    while True:
        # Get IP address from user
        ip = input("\nPlease enter an IP address (or 'quit' to exit): ").strip()
        
        if ip.lower() in ['quit', 'exit', 'q']:
            print("\nThank you for using Device Info Finder!")
            sys.exit(0)
            
        if not is_valid_ip(ip):
            print("Error: Invalid IP address format. Please try again.")
            continue
            
        # Get and display device information
        info = get_device_name(ip)
        print_device_info(info)
        
        # Ask if user wants to check another IP
        choice = input("\nWould you like to check another IP? (y/n): ").strip().lower()
        if choice != 'y':
            print("\nThank you for using Device Info Finder!")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        sys.exit(1)