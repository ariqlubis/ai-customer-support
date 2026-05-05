resource "google_bigquery_dataset" "faq_dataset" {
    dataset_id = "faq_data"
    friendly_name = "FAQ Dataset"
    description = "Dataset for storing FAQ data"
    location = var.region
    delete_contents_on_destroy = true
}

resource "google_bigquery_table" "faq_table" {
    dataset_id = google_bigquery_dataset.faq_dataset.dataset_id
    table_id = "faqs"
    deletion_protection = false

    schema = <<EOF
[
  {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
  {"name": "category", "type": "STRING", "mode": "NULLABLE"},
  {"name": "question", "type": "STRING", "mode": "REQUIRED"},
  {"name": "answer", "type": "STRING", "mode": "REQUIRED"},
  {"name": "embedding", "type": "FLOAT64", "mode": "REPEATED"},
  {"name": "source", "type": "STRING", "mode": "NULLABLE"},
  {"name": "language", "type": "STRING", "mode": "NULLABLE"}
]
EOF
}

resource "google_artifact_registry_repository" "app_repo" {
    location = var.region
    repository_id = "ai-support-app"
    description = "Docker Repository for AI Customer Support App"
    format = "DOCKER"
}

resource "google_cloud_run_v2_service" "rag_service" {
    name = "ai-support-chatbot"
    location = var.region
    ingress = "INGRESS_TRAFFIC_ALL"
    template {
        containers {
            image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.app_repo.repository_id}/app-image:latest"
            env {
                name = "PROJECT_ID"
                value = var.project_id
            }
            env {
                name = "LOCATION"
                value = var.region
            }
        }
    }

    lifecycle {
        ignore_changes = [ 
            client,
            client_version,
            template[0].containers[0].image
         ]
    }
}

resource "google_cloud_run_service_iam_member" "public_access" {
    service = google_cloud_run_v2_service.rag_service.name
    location = google_cloud_run_v2_service.rag_service.location
    role = "roles/run.invoker"
    member = "allUsers"
}