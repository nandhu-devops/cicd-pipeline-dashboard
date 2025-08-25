"""
🔐 Secret Manager - OpenSSL-based encryption/decryption for sensitive values
"""

import os
import subprocess
import base64
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class SecretManager:
    """Manages encrypted secrets using OpenSSL AES-256-CBC encryption"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """Initialize with base directory (defaults to parent of current file)"""
        if base_dir is None:
            # Default to project root (3 levels up: app -> backend -> project)
            base_dir = Path(__file__).parent.parent.parent
        
        self.base_dir = Path(base_dir)
        self.secrets_dir = self.base_dir / ".secrets"
        self.key_file = self.base_dir / ".encryption_key"
        
        # Ensure directories exist
        self.secrets_dir.mkdir(mode=0o700, exist_ok=True)
        
        # Cache for decrypted secrets (in memory only)
        self._cache: Dict[str, str] = {}
        
        logger.info(f"🔐 SecretManager initialized - secrets dir: {self.secrets_dir}")
    
    def _get_encryption_key(self) -> str:
        """Get the master encryption key"""
        try:
            with open(self.key_file, 'r') as f:
                key = f.read().strip()
                if not key:
                    raise ValueError("Encryption key file is empty")
                return key
        except FileNotFoundError:
            raise FileNotFoundError(f"Encryption key not found at {self.key_file}")
        except Exception as e:
            raise RuntimeError(f"Failed to read encryption key: {e}")
    
    def decrypt_secret(self, secret_name: str, use_cache: bool = True) -> str:
        """
        Decrypt a secret by name
        
        Args:
            secret_name: Name of the secret (without .enc extension)
            use_cache: Whether to use cached decrypted value
            
        Returns:
            Decrypted secret value
            
        Raises:
            FileNotFoundError: If encrypted file doesn't exist
            RuntimeError: If decryption fails
        """
        # Check cache first
        if use_cache and secret_name in self._cache:
            return self._cache[secret_name]
        
        encrypted_file = self.secrets_dir / f"{secret_name}.enc"
        
        if not encrypted_file.exists():
            raise FileNotFoundError(f"Encrypted secret not found: {encrypted_file}")
        
        try:
            # Get encryption key
            key = self._get_encryption_key()
            
            # Decrypt using OpenSSL
            cmd = [
                'openssl', 'enc', '-d',
                '-aes-256-cbc', '-a', '-salt',
                '-pass', f'pass:{key}',
                '-in', str(encrypted_file)
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True,
                timeout=10
            )
            
            decrypted_value = result.stdout.strip()
            
            if not decrypted_value:
                raise ValueError(f"Decrypted value is empty for secret: {secret_name}")
            
            # Cache the decrypted value
            if use_cache:
                self._cache[secret_name] = decrypted_value
            
            logger.info(f"🔓 Successfully decrypted secret: {secret_name}")
            return decrypted_value
            
        except subprocess.CalledProcessError as e:
            error_msg = f"OpenSSL decryption failed for {secret_name}: {e.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except subprocess.TimeoutExpired:
            error_msg = f"Decryption timeout for secret: {secret_name}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error decrypting {secret_name}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def encrypt_secret(self, secret_name: str, value: str) -> None:
        """
        Encrypt and store a secret
        
        Args:
            secret_name: Name of the secret (without .enc extension)
            value: The secret value to encrypt
        """
        encrypted_file = self.secrets_dir / f"{secret_name}.enc"
        
        try:
            # Get encryption key
            key = self._get_encryption_key()
            
            # Encrypt using OpenSSL
            cmd = [
                'openssl', 'enc',
                '-aes-256-cbc', '-a', '-salt',
                '-pass', f'pass:{key}',
                '-out', str(encrypted_file)
            ]
            
            result = subprocess.run(
                cmd,
                input=value,
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            
            logger.info(f"🔒 Successfully encrypted secret: {secret_name}")
            
            # Remove from cache if it exists
            self._cache.pop(secret_name, None)
            
        except subprocess.CalledProcessError as e:
            error_msg = f"OpenSSL encryption failed for {secret_name}: {e.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error encrypting {secret_name}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def list_secrets(self) -> list:
        """List all available encrypted secrets"""
        try:
            secrets = []
            for file in self.secrets_dir.glob("*.enc"):
                secrets.append(file.stem)  # filename without .enc extension
            return sorted(secrets)
        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def secret_exists(self, secret_name: str) -> bool:
        """Check if a secret exists"""
        encrypted_file = self.secrets_dir / f"{secret_name}.enc"
        return encrypted_file.exists()
    
    def clear_cache(self) -> None:
        """Clear the in-memory cache of decrypted secrets"""
        self._cache.clear()
        logger.info("🗑️ Secret cache cleared")

# Global instance
secret_manager = SecretManager()

def get_secret(name: str) -> str:
    """Convenience function to get a secret"""
    return secret_manager.decrypt_secret(name)

def get_secret_or_env(secret_name: str, env_var: str, default: str = None) -> Optional[str]:
    """
    Try to get secret from encrypted store, fallback to environment variable
    
    Args:
        secret_name: Name of encrypted secret
        env_var: Environment variable name  
        default: Default value if neither found
        
    Returns:
        Secret value or default
    """
    try:
        # Try encrypted secret first
        if secret_manager.secret_exists(secret_name):
            return secret_manager.decrypt_secret(secret_name)
    except Exception as e:
        logger.warning(f"Failed to decrypt {secret_name}: {e}")
    
    # Fallback to environment variable
    env_value = os.getenv(env_var)
    if env_value:
        return env_value
    
    # Return default
    return default
