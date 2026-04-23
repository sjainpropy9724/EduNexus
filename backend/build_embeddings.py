"""
Build Semantic Index — run once after data ingestion.

Run from EduNexus_v2/backend/:
    python build_embeddings.py
"""

from app.services.vector_store import vector_store

if __name__ == "__main__":
    print("🚀 Building semantic embedding index...")
    result = vector_store.build_index(batch_size=256)

    print("\n📊 Index Stats:")
    stats = vector_store.get_index_stats()
    print(f"   Total skills:    {stats['total_skills']}")
    print(f"   Embedded skills: {stats['embedded_skills']}")
    print(f"   Coverage:        {stats['coverage_pct']}%")
    print(f"   Index ready:     {stats['index_ready']}")

    if stats["index_ready"]:
        print("\n✅ Semantic index ready. Hybrid gap analysis is now available.")
        print("   Test it: GET /api/v1/audit/research_report?use_hybrid=true")
    else:
        print("\n❌ Index build failed. Check logs above.")
