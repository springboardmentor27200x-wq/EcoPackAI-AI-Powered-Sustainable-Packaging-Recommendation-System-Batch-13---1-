let currentResults = [];
let costChart, co2Chart;

async function getRecommendation() {
    const data = {
        product_name: document.getElementById("product_name").value,
        weight: document.getElementById("weight").value,
        industry: document.getElementById("industry").value,
        fragility_level: document.getElementById("fragility").value,
        shipping_type: document.getElementById("shipping").value,
        safety_requirement: document.getElementById("safety").value
    };

    if (!data.product_name || !data.weight) {
        alert("Please enter Product Name and Weight.");
        return;
    }

    try {
        // Log to Database (Milestone 3)
        await fetch("/add_product", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        // Get AI Recommendations
        const response = await fetch("/recommend", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        
        let results = await response.json();

        // --- Milestone 4 Fix: Remove Duplicate Material Names ---
        const uniqueMaterials = [];
        const seenNames = new Set();
        results.forEach(item => {
            if (!seenNames.has(item.material_name)) {
                seenNames.add(item.material_name);
                uniqueMaterials.push(item);
            }
        });
        
        currentResults = uniqueMaterials;

        // Update Table
        let rows = "";
        currentResults.forEach(mat => {
            rows += `<tr>
                <td class="fw-bold">${mat.material_name}</td>
                <td>$${mat.predicted_cost.toFixed(2)}</td>
                <td>${mat.predicted_co2.toFixed(2)} kg/CO2</td>
                <td><span class="badge bg-success">${(mat.rank_score * 100).toFixed(1)}%</span></td>
            </tr>`;
        });
        document.getElementById("result_table").innerHTML = rows;

        // Update BI Dashboard Charts
        updateCharts(currentResults);

    } catch (err) {
        console.error(err);
        alert("Error connecting to server.");
    }
}

function updateCharts(results) {
    const labels = results.map(r => r.material_name);
    const costs = results.map(r => r.predicted_cost);
    const co2 = results.map(r => r.predicted_co2);

    if (costChart) costChart.destroy();
    if (co2Chart) co2Chart.destroy();

    costChart = new Chart(document.getElementById('costChart'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{ label: 'Unit Cost ($)', data: costs, backgroundColor: '#3498db' }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    co2Chart = new Chart(document.getElementById('co2Chart'), {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{ label: 'CO2 Footprint', data: co2, backgroundColor: ['#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6', '#34495e'] }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

// --- Milestone 4 Requirement: PDF Generation ---
function exportToPDF() {
    if (currentResults.length === 0) {
        alert("No data to export. Please generate insights first.");
        return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const pName = document.getElementById("product_name").value || "Product";

    // PDF Header
    doc.setFontSize(18);
    doc.text("EcoPackAI Sustainability Report", 14, 20);
    doc.setFontSize(12);
    doc.text(`Target Product: ${pName}`, 14, 30);
    doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 14, 37);

    // Prepare Table Data
    const tableBody = currentResults.map(r => [
        r.material_name,
        `$${r.predicted_cost.toFixed(2)}`,
        `${r.predicted_co2.toFixed(2)} kg`,
        `${(r.rank_score * 100).toFixed(1)}%`
    ]);

    // Add Table
    doc.autoTable({
        startY: 45,
        head: [['Material', 'Predicted Cost', 'CO2 Impact', 'Sustainability Rank']],
        body: tableBody,
        theme: 'striped',
        headStyles: { fillColor: [39, 174, 96] }
    });

    doc.save(`EcoPackAI_Report_${pName}.pdf`);
}

function exportToCSV() {
    if (currentResults.length === 0) return alert("No data!");
    let csv = "Material,Cost,CO2,Rank\n";
    currentResults.forEach(r => {
        csv += `${r.material_name},${r.predicted_cost},${r.predicted_co2},${r.rank_score}\n`;
    });
    const link = document.createElement("a");
    link.href = 'data:text/csv;charset=utf-8,' + encodeURI(csv);
    link.target = '_blank';
    link.download = 'EcoPackAI_Report.csv';
    link.click();
}

