import bcrypt

def encriptar_clave(password):
    """
    Toma una contraseña en texto plano (ej: 'admin123') 
    y la convierte en un hash de seguridad ilegible.
    """
    # Generar la 'sal' (salt) para que el hash sea único aunque la clave sea igual
    salt = bcrypt.gensalt()
    # Encriptar
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Devolver como string para que se pueda guardar en Excel
    return hashed.decode('utf-8')

def verificar_clave(password_ingresada, hashed_password_guardada):
    """
    Compara la clave que el usuario escribe en el login 
    con la clave encriptada que tenemos en el Excel.
    """
    try:
        # Verificamos si la clave coincide
        return bcrypt.checkpw(
            password_ingresada.encode('utf-8'), 
            hashed_password_guardada.encode('utf-8')
        )
    except Exception:
        # Si la clave del Excel no está encriptada (formato viejo), 
        # devolvemos False para evitar que el programa se cierre.
        return False