from supabase_utils import sync_model_files

sync_model_files()

docker run -d -p 8080:8000 \
  -e SUPABASE_URL="https://hrmwenjncgrqvfaoawep.supabase.co" \
  -e SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhybXdlbmpuY2dycXZmYW9hd2VwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzE5ODI0OSwiZXhwIjoyMDYyNzc0MjQ5fQ.Fq8fawVCRRBPaOF-1gcUAornIk7VMbe2EFfrDS3Wquk" \
  -e SUPABASE_MODEL_BUCKET="models" \
  ers-image-classifier