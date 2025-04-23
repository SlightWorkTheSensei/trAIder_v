package main

import (
	"encoding/csv"
	"fmt"
	"html/template"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

type AppData struct {
	ID   string
	Name string
	URL  string
}

type DashboardData struct {
	Apps []AppData
}

// Function to start a Flask app
func startFlaskApp(appPath string, port string) {
	fmt.Printf("Starting Flask App (%s) on port %s...\n", appPath, port)

	dir, file := filepath.Split(appPath)
	cmd := exec.Command("python", file)
	cmd.Dir = dir

	env := append(os.Environ(), fmt.Sprintf("FLASK_RUN_PORT=%s", port))
	cmd.Env = env

	err := cmd.Start()
	if err != nil {
		fmt.Printf("Error starting Flask App (%s): %v\n", appPath, err)
	}
}

// Function to read app paths and ports from a CSV file
func readAppPathsWithPorts(filePath string) ([]AppData, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, fmt.Errorf("error opening CSV file: %v", err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, fmt.Errorf("error reading CSV file: %v", err)
	}

	var apps []AppData
	for i, record := range records {
		if len(record) == 2 {
			name := strings.TrimSpace(record[0])
			port := strings.TrimSpace(record[1])
			apps = append(apps, AppData{
				ID:   fmt.Sprintf("app-container-%d", i),
				Name: name,
				URL:  fmt.Sprintf("http://127.0.0.1:%s", port),
			})
		}
	}
	return apps, nil
}

// Function to serve the dashboard
func serveDashboard(apps []AppData) {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		tmpl := `
		<!DOCTYPE html>
		<html lang="en">
		<head>
			<meta charset="UTF-8">
			<meta name="viewport" content="width=device-width, initial-scale=1.0">
			<title>Flask Apps Dashboard</title>
			<style>
				body {
					background-color: black;
					color: lime;
					font-family: monospace;
					margin: 0;
					padding: 0;
				}
				h1 {
					text-align: center;
					text-shadow: 0px 0px 5px lime;
					margin-top: 20px;
				}
				.container {
					display: flex;
					flex-wrap: wrap;
					justify-content: center;
					margin: 20px;
				}
				.iframe-container {
					width: 45%;
					height: 90%;
					margin: 20px;
					padding: 10px;
					border: 2px solid lime;
					box-shadow: 0px 0px 10px lime;
					background-color: black;
					position: relative;
					transition: transform 0.3s ease;
				}
				iframe {
					width: 100%;
					height: 80%;
					border: none;
				}
				.app-title {
					text-align: center;
					margin-bottom: 10px;
					text-shadow: 0px 0px 5px lime;
				}
				.full-screen {
					position: fixed;
					top: 0;
					left: 0;
					width: 100%;
					height: 100%;
					z-index: 9999;
					background-color: black;
					border: none;
					display: flex;
					flex-direction: column;
					justify-content: center;
					align-items: center;
				}
			</style>
			<script>
				function toggleExpand(containerId, button) {
					const container = document.getElementById(containerId);
					if (container.classList.contains('full-screen')) {
						// Shrink
						container.classList.remove('full-screen');
						button.textContent = 'Expand';
					} else {
						// Expand
						container.classList.add('full-screen');
						button.textContent = 'Shrink';
					}
				}
			</script>
		</head>
		<body>
			<h1>Go-Flask Trading Dashboard</h1>
			<br>
			<h1>From Algorithmic Investment Solutions LLC</h1>
			<div class="container">
				{{range .Apps}}
				<div class="iframe-container" id="{{.ID}}">
					<h3 class="app-title">{{.Name}}</h3>
					<iframe src="{{.URL}}"></iframe>
					<button onclick="toggleExpand('{{.ID}}', this)">Expand</button>
				</div>
				{{end}}
			</div>
		</body>
		</html>`
		t, err := template.New("dashboard").Parse(tmpl)
		if err != nil {
			fmt.Fprintf(w, "Error rendering template: %v", err)
			return
		}

		data := DashboardData{Apps: apps}
		t.Execute(w, data)
	})

	fmt.Println("Serving dashboard on http://127.0.0.1:8085")
	http.ListenAndServe(":8085", nil)
}

func main() {
	// Read Flask app paths and ports from CSV
	records, err := readAppPathsWithPorts("./csv/app_paths.csv")
	if err != nil {
		fmt.Println("Error reading app paths with ports:", err)
		return
	}

	// Start Flask apps
	for _, app := range records {
		go startFlaskApp(app.Name, app.URL[len("http://127.0.0.1:"):])
		time.Sleep(1 * time.Second) // Slight delay to avoid race conditions
	}

	// Serve the HTML dashboard
	serveDashboard(records)
}
