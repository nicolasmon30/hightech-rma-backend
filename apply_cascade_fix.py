"""
Script para aplicar el fix de CASCADE DELETE a password_reset_tokens
Ejecutar: python apply_cascade_fix.py
"""
import os
from sqlalchemy import create_engine, text

# Obtener DATABASE_URL de las variables de entorno de Railway
database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("❌ ERROR: No se encontró DATABASE_URL")
    print("Copia el DATABASE_URL de Railway y ejecuta:")
    print('$env:DATABASE_URL="postgresql://..." (Windows PowerShell)')
    print("Luego vuelve a ejecutar este script")
    exit(1)

print(f"🔗 Conectando a la base de datos...")

try:
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        # 1. Eliminar constraint existente
        print("🗑️  Eliminando constraint antigua...")
        conn.execute(text("""
            ALTER TABLE password_reset_tokens 
            DROP CONSTRAINT IF EXISTS password_reset_tokens_user_id_fkey;
        """))
        conn.commit()
        
        # 2. Crear nueva constraint con CASCADE
        print("✨ Creando nueva constraint con CASCADE...")
        conn.execute(text("""
            ALTER TABLE password_reset_tokens
            ADD CONSTRAINT password_reset_tokens_user_id_fkey 
            FOREIGN KEY (user_id) 
            REFERENCES users(id) 
            ON DELETE CASCADE;
        """))
        conn.commit()
        
        # 3. Verificar
        print("🔍 Verificando...")
        result = conn.execute(text("""
            SELECT 
                conname AS constraint_name,
                confdeltype AS delete_action
            FROM pg_constraint
            WHERE conname = 'password_reset_tokens_user_id_fkey';
        """))
        
        row = result.fetchone()
        if row and row[1] == 'c':
            print("✅ ¡SUCCESS! CASCADE DELETE configurado correctamente")
            print("Ahora puedes eliminar usuarios sin problemas")
        else:
            print("⚠️  Algo salió mal, verifica manualmente")
            
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nAsegúrate de que DATABASE_URL esté correctamente configurada")
