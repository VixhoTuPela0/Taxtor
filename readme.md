
# Taxtor

Una aplicacion hecha para mi papa para que pueda guardar las cuentas bien. Detecta tu posicion, si es probable que hiciste una compra y te pide que la almacenes, se hace desde el telefono pero se puede consultar desde el mismo o un computador


## Funciones
- Sistema de cuentas (Commit 1/2) Listo
- Guardar facturas
- Subir fotos, fechas, tarjeta...
- Exportar excel

Todo eso es a venir. En el momento que escribo esto (commit 2) el sistema de login esta completo, con un login y register funcional y seguro, cookies, etc....
## Updates
### Commit 1
en el commit 1 el sistema de register fue hecho, con un fetch register con FastAPI, y una pagina basica que te dejaba registrarte.
### Commit 2
Sistema de cuentas finalizado, register sigue terminado, login fue concluido y las contrasenas son hasheadas, despues al logear se queda una cookie con la sesion durante 7 dias. Una pagina basica de home para ver que sigues logeado, tambien un logout para borrar la sesion del dispositivo y la base de datos.