-- Script para agregar CASCADE DELETE a password_reset_tokens
-- Ejecutar este script directamente en la base de datos de producción

-- 1. Eliminar la constraint existente
ALTER TABLE password_reset_tokens 
DROP CONSTRAINT IF EXISTS password_reset_tokens_user_id_fkey;

-- 2. Agregar la nueva constraint con CASCADE
ALTER TABLE password_reset_tokens
ADD CONSTRAINT password_reset_tokens_user_id_fkey 
FOREIGN KEY (user_id) 
REFERENCES users(id) 
ON DELETE CASCADE;

-- 3. Verificar que la constraint se creó correctamente
SELECT 
    conname AS constraint_name,
    confdeltype AS delete_action
FROM pg_constraint
WHERE conname = 'password_reset_tokens_user_id_fkey';

-- Si delete_action es 'c', significa CASCADE está configurado correctamente
