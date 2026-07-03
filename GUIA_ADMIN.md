# 🎀 Guía de Administración — Detalles Aleydy

> **Última actualización:** 3 de julio de 2026
> **Responsable:** Will (Hermes) — dvill007
> **Marca:** Aleydy — detalles personalizados en Pucallpa

---

## 📋 Resumen Ejecutivo

Detalles Aleydy vende ramos eternos, boxes y detalles personalizados en Pucallpa. Todo el ecosistema está construido para ser **ultra-simple**: una landing page, un dashboard local de administración, y WhatsApp como canal único de ventas.

| Componente | Estado | Ubicación |
|---|---|---|
| Landing page | 🟢 Vivo | https://detalles-aleydy.vercel.app |
| Dashboard admin | 🟢 Local | `http://localhost:5050` |
| Base de datos | 🟢 Firestore | Google Cloud `detalles-aleydy` |
| Analytics | 🟡 Parcial | GA4 activo, Facebook Pixel pendiente |
| Redes sociales | 🟢 Activo | Instagram + TikTok: @aleydy_1 |

---

## 🏗️ Arquitectura del Ecosistema

```
┌─────────────────────────────────────────────────┐
│                  CLIENTE FINAL                    │
│  Ve la landing → Manda WhatsApp → Recibe pedido  │
└────────────────────┬────────────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
┌─────────┐   ┌────────────┐   ┌──────────┐
│ Vercel  │   │  WhatsApp   │   │ RRSS     │
│ Landing │   │  +51 931    │   │ IG + TT  │
│ (HTML)  │   │  699 656    │   │ @aleydy_1│
└────┬────┘   └────────────┘   └──────────┘
     │
     │ Analytics
     ▼
┌─────────┐   ┌────────────┐   ┌──────────┐
│  GA4    │   │  Firestore │   │ Dashboard│
│ G-R0CJP │   │  20 prod.  │◄──│ :5050    │
│  484CY  │   │  4 categ.  │   │ admin.py │
└─────────┘   └────────────┘   └──────────┘
```

---

## 🌐 1. Landing Page

### Datos Clave

| Campo | Valor |
|---|---|
| URL | `https://detalles-aleydy.vercel.app` |
| Repositorio | `github.com/dvill007/detalles-aleydy` |
| Hosting | Vercel (conectado al repo, deploy automático) |
| Rama deploy | `main` |
| Tecnología | HTML estático + Tailwind CSS CDN |

### ¿Cómo actualizar el catálogo?

**Opción A — Dashboard (recomendado):** Iniciá el dashboard local y editá productos desde la UI.

**Opción B — Manual:** Editá `index.html` directamente. Cada producto es un `<div class="product-card">`. Hacé commit y push, Vercel redeploya solo.

```bash
cd ~/repos/detalles-aleydy
# Editar index.html
git add index.html
git commit -m "Actualizar catálogo"
git push origin main
```

**⚠️ Importante:** Las fotos van en `assets/images/`. Usá JPG para originales y WebP para optimizadas.

### Catálogo Actual (20 productos en 4 categorías)

| Categoría | Productos | Rango Precio |
|---|---|---|
| 🌹 Ramos Clásicos | 4 | S/20 – S/280 |
| 🦋 Ramos Especiales | 5 | S/20 – S/55 |
| 🎀 Ramos Temáticos | 7 | S/25 – S/65 |
| 📦 Boxes Temáticos | 4 | S/50 – S/60 |

### SEO y Datos Estructurados

- **Schema.org:** `LocalBusiness` con productos, precios, horarios
- **Open Graph:** Título, descripción, imagen para WhatsApp/Facebook
- **Meta tags:** description, keywords, canonical URL
- **Archivo:** `structured-data.json` (datos para Google)

### Sistema de Urgencia

La página tiene un banner automático que se activa según:
- **Antes de 3 PM:** "Pide antes de las 3 PM y recibe HOY"
- **Fechas especiales:** 7 días antes de San Valentín, Día de la Madre, Padre, Fiestas Patrias, Amistad, Navidad
- **Noche (3-8 PM):** "¿Pedido urgente para mañana?"
- Los badges "⚡ Entrega hoy" aparecen automáticamente en todos los productos

---

## 📊 2. Analytics

### Google Analytics 4
- **ID:** `G-R0CJP484CY`
- **Estado:** 🟢 Activo
- **Dashboard:** https://analytics.google.com → cuenta de Aleydy
- **Eventos trackeados:** PageView, clicks en WhatsApp (conversiones)

### Facebook Pixel
- **ID:** `000000000000000` (placeholder)
- **Estado:** 🔴 NO ACTIVO
- **Para activar:** Crear un Pixel en Facebook Business → reemplazar el ID en `index.html` (líneas 100 y 104)

---

## 🛒 3. Canal de Ventas — WhatsApp

- **Número:** `+51 931 699 656`
- **Flujo:** El cliente ve un producto → toca "Pedir" → se abre chat de WhatsApp con mensaje pre-escrito
- **Formato mensaje:** `"Hola, quiero el [Nombre Producto] 🎀"`
- **Sin carrito:** No hay checkout online. Todo se coordina por chat.

---

## 📱 4. Redes Sociales

| Plataforma | Usuario | URL |
|---|---|---|
| Instagram | @aleydy_1 | https://www.instagram.com/aleydy_1 |
| TikTok | @aleydy_1 | https://www.tiktok.com/@aleydy_1 |

Los íconos están en el footer de la landing.

---

## 🖥️ 5. Dashboard de Administración

### Arranque

```bash
cd ~/repos/detalles-aleydy
./start.sh
```

Abrir navegador en: **http://localhost:5050**
Token de acceso: **`aleydy-admin-2026`**

### Funciones

| Tab | ¿Qué hace? |
|---|---|
| 📦 Productos | Ver, crear, editar, eliminar productos (nombre, precio, foto, badge, categoría, destacado, activo) |
| 📋 Pedidos | Ver pedidos con estado (nuevo → preparando → listo → entregado → cancelado) |
| 🏷️ Categorías | Gestionar categorías y su orden de aparición |

### Base de Datos (Firestore)

- **Proyecto Google Cloud:** `detalles-aleydy` (#740798104493)
- **Zona:** `southamerica-east1` (São Paulo)
- **Colecciones:**
  - `productos` — 20 documentos
  - `categorias` — 4 documentos
  - `pedidos` — (vacío, se llena con pedidos)
- **Service Account:** `aleydyosco@detalles-aleydy.iam.gserviceaccount.com`
- **Clave:** `~/.hermes/keys/detalles-aleydy-firebase-sa.json`

### Cómo agregar un pedido manualmente

Desde el dashboard no hay botón "Nuevo pedido" aún. Para registrar un pedido manualmente, avisame (Cortana) o usá este comando:

```bash
python3 -c "
from firebase_admin import credentials, firestore
import firebase_admin as fb

cred = credentials.Certificate('/home/will/.hermes/keys/detalles-aleydy-firebase-sa.json')
try: fb.get_app(); fb.delete_app(fb.get_app())
except: pass
fb.initialize_app(cred)
db = firestore.client()

db.collection('pedidos').add({
    'cliente': 'Nombre Cliente',
    'telefono': '999888777',
    'producto': 'Ramo Básico',
    'total': 45,
    'estado': 'nuevo',
    'fecha': firestore.SERVER_TIMESTAMP
})
print('Pedido registrado ✅')
"
```

---

## 🔄 6. Pipeline de Operación Diaria

```
MAÑANA (9 AM)
  └─ Iniciar dashboard: ./start.sh
  └─ Revisar pedidos nuevos en tab "📋 Pedidos"

DURANTE EL DÍA
  └─ WhatsApp: responder consultas
  └─ Dashboard: cambiar estado de pedidos (preparando → listo → entregado)
  └─ Si entra producto nuevo:
      └─ Foto → assets/images/
      └─ Dashboard → + Nuevo Producto

NOCHE (8 PM)
  └─ Dashboard: revisar pendientes
  └─ Cerrar dashboard: CTRL+C
  └─ Opcional: revisar GA4 para métricas del día
```

---

## 🔮 7. Próximos Pasos (Roadmap)

| Prioridad | Tarea | Bloqueante |
|---|---|---|
| 🔴 P0 | Activar Facebook Pixel | Crear Pixel en Facebook Business |
| 🟡 P1 | Activar Firebase Auth (login email/password) | Billing en GCP (tarjeta) |
| 🟡 P1 | Dashboard accesible sin localhost | Deploy del dashboard (Vercel o Firebase Hosting) |
| 🟢 P2 | Formulario de pedidos en la landing | — |
| 🟢 P2 | Catálogo dinámico (cargar desde Firestore en vez de HTML) | — |
| 🟢 P3 | Fotos de productos pendientes (5 sin foto) | Sesión de fotos |

---

## 🔐 8. Credenciales y Accesos

| Recurso | Dónde está | Notas |
|---|---|---|
| Service Account Firebase | `~/.hermes/keys/detalles-aleydy-firebase-sa.json` | No compartir, permisos 600 |
| Token dashboard | `aleydy-admin-2026` | Cambiable en `admin.py` línea 22 |
| API Key Firebase Web | `firebase-config.js` | Es pública, va en el frontend |
| GitHub repo | `dvill007/detalles-aleydy` | Deploy automático a Vercel |
| Google Analytics | Cuenta Google de Aleydy | G-R0CJP484CY |
| WhatsApp Business | +51 931 699 656 | Número de Aleydy |

---

## 🆘 9. Solución de Problemas

### "El dashboard no carga"
```bash
# Verificar que el servidor está corriendo
curl http://localhost:5050/api/auth/check
# Si no responde: ./start.sh
```

### "No se guardan los cambios de productos"
- Verificar que `keys/detalles-aleydy-firebase-sa.json` existe
- Revisar conexión a internet (Firestore es cloud)

### "La landing no se actualiza"
- Vercel tarda ~30 segundos en deployar después del push
- Verificar en https://vercel.com/dvill007 (dashboard de Vercel)

### "Necesito ayuda con algo más complejo"
- Hablar con Cortana (yo) vía Telegram

---

> *"Tú eliges el color, nosotras lo creamos con amor."* 🎀
