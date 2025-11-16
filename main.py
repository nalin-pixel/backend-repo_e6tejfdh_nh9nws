import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from database import db, create_document
from schemas import ContactMessage

app = FastAPI(title="EcoCampus API", description="Backend for EcoCampus portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "EcoCampus Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# -------- Static educational content endpoints --------
class Article(BaseModel):
    slug: str
    title: str
    excerpt: str
    content: str

ARTICLES: List[Article] = [
    Article(
        slug="kelola-sampah-kampus",
        title="Cara Mengelola Sampah di Kampus",
        excerpt="Tips praktis memilah, mengurangi, dan mengolah sampah di lingkungan kampus",
        content="Langkah-langkah: 1) Pisahkan organik, anorganik, dan residu. 2) Gunakan tumbler. 3) Dorong bank sampah kampus."
    ),
    Article(
        slug="hemat-energi-gedung",
        title="Menghemat Energi di Gedung Kuliah",
        excerpt="Kebiasaan sederhana yang mengurangi konsumsi listrik dan jejak karbon",
        content="Matikan lampu saat keluar ruangan, atur AC 24-26°C, manfaatkan cahaya alami, dan lakukan audit energi berkala."
    ),
    Article(
        slug="plastik-jadi-karya",
        title="Mengubah Limbah Plastik jadi Karya Seni",
        excerpt="Inspirasi upcycle untuk pameran dan kegiatan seni mahasiswa",
        content="Kumpulkan botol bekas, bersihkan, potong sesuai pola, gabungkan menjadi instalasi seni bertema lingkungan."
    )
]

class GalleryItem(BaseModel):
    id: str
    title: str
    category: str
    image: str

GALLERY: List[GalleryItem] = [
    GalleryItem(id="1", title="Aksi Menanam Pohon", category="Aksi", image="/images/tree-planting.jpg"),
    GalleryItem(id="2", title="Gerakan Kampus Bebas Plastik", category="Kampanye", image="/images/plastic-free.jpg"),
    GalleryItem(id="3", title="Workshop Daur Ulang", category="Workshop", image="/images/recycle-workshop.jpg"),
    GalleryItem(id="4", title="Hari Bersih Kampus", category="Komunitas", image="/images/campus-cleanup.jpg"),
]

@app.get("/api/articles", response_model=List[Article])
def get_articles():
    return ARTICLES

@app.get("/api/articles/{slug}", response_model=Article)
def get_article(slug: str):
    for a in ARTICLES:
        if a.slug == slug:
            return a
    raise HTTPException(status_code=404, detail="Artikel tidak ditemukan")

@app.get("/api/gallery", response_model=List[GalleryItem])
def get_gallery():
    return GALLERY

# -------- Contact form --------
@app.post("/api/contact")
def submit_contact(payload: ContactMessage):
    try:
        doc_id = create_document("contactmessage", payload)
        return {"status": "ok", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
