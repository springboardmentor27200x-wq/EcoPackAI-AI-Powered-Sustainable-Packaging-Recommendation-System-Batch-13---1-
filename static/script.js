// ================= VARIATIONS =================
function generateVariations(data){
let expanded = [];

data.forEach(item => {

expanded.push(item);

// Eco
expanded.push({
...item,
material: item.material + " (Eco)",
predicted_co2: Math.max(1, item.predicted_co2 - 5),
score: item.score + 0.03
});

// Premium
expanded.push({
...item,
material: item.material + " (Premium)",
predicted_cost: item.predicted_cost + 8
});

// Lightweight
expanded.push({
...item,
material: item.material + " (Lightweight)",
predicted_cost: Math.max(1, item.predicted_cost - 5)
});

});

return expanded;
}


// ================= FILTER =================
function applyFilter(data, type){

if(type==="eco"){
return data.sort((a,b)=>a.predicted_co2 - b.predicted_co2);
}
if(type==="cheap"){
return data.sort((a,b)=>a.predicted_cost - b.predicted_cost);
}
if(type==="strong"){
return data.sort((a,b)=>b.score - a.score);
}

return data;
}


// ================= MAIN =================
function getRecommendation(){

console.log("BUTTON CLICKED 🔥");

let tbody = document.getElementById("resultTable");
tbody.innerHTML = "";

let topN = parseInt(document.getElementById("topN").value) || 3;
let filter = document.getElementById("filterType").value;

// BASE DATA
let base = [
{material:"Corrugated Box",score:0.91,predicted_cost:45,predicted_co2:22},
{material:"Molded Fiber",score:0.88,predicted_cost:50,predicted_co2:18},
{material:"Bioplastic",score:0.82,predicted_cost:60,predicted_co2:25},
{material:"Recycled Paper",score:0.79,predicted_cost:48,predicted_co2:20}
];

// APPLY VARIATIONS
let data = generateVariations(base);

// APPLY FILTER
data = applyFilter(data, filter);

// TAKE TOP N
let result = data.slice(0, topN);

// DEBUG
console.log("FINAL RESULT:", result);

// TABLE
result.forEach((x,index)=>{
tbody.innerHTML += `
<tr class="fade-row" style="animation-delay:${index*0.1}s">
<td>${x.material}</td>
<td>${x.score.toFixed(2)}</td>
<td>${x.predicted_cost}</td>
<td>${x.predicted_co2}</td>
</tr>`;
});

// SHOW BUTTONS
document.getElementById("pdfBtn").style.display="block";
document.getElementById("excelBtn").style.display="block";

// UPDATE DASHBOARD
updateDashboard(result);
}


// ================= DASHBOARD =================
function updateDashboard(data){

if(!data || data.length === 0){
console.log("No data for dashboard");
return;
}

let materials = data.map(x=>x.material);
let co2 = data.map(x=>x.predicted_co2);
let cost = data.map(x=>x.predicted_cost);

// DEBUG
console.log("CO2:", co2);
console.log("COST:", cost);

// CHARTS
Plotly.newPlot("co2Chart",[{
x:materials,
y:co2,
type:"bar"
}], {title:"CO₂ Comparison"});

Plotly.newPlot("costChart",[{
x:materials,
y:cost,
type:"bar"
}], {title:"Cost Comparison"});

Plotly.newPlot("materialChart",[{
labels:materials,
values:co2,
type:"pie"
}], {title:"Material Distribution"});

// CALCULATIONS
let total = co2.reduce((a,b)=>a+b,0);
let avg = cost.reduce((a,b)=>a+b,0)/cost.length;

let max = Math.max(...co2);
let min = Math.min(...co2);
let reduction = ((max - min) / max) * 100;

// KPI UPDATE 🔥
document.getElementById("kpiCo2").innerText = total.toFixed(2);
document.getElementById("kpiCost").innerText = avg.toFixed(2);
document.getElementById("kpiReduction").innerText = reduction.toFixed(2) + "%";

// INSIGHTS
document.getElementById("insights").innerHTML =
"🌍 Total CO₂: " + total.toFixed(2) +
" | 💰 Avg Cost: " + avg.toFixed(2) +
"<br>🌱 Reduction: " + reduction.toFixed(2) + "%";
}


// ================= PDF =================
async function downloadPDF(){

const { jsPDF } = window.jspdf;
let doc = new jsPDF();

doc.text("EcoPack Report",20,20);

let rows = document.querySelectorAll("#resultTable tr");
let y=40;

rows.forEach(r=>{
doc.text(r.innerText,20,y);
y+=8;
});

let insights = document.getElementById("insights").innerText;

doc.text("Insights:",20,y+10);
doc.text(insights,20,y+18);

doc.save("report.pdf");
}


// ================= EXCEL =================
function downloadExcel(){

let rows = document.querySelectorAll("#resultTable tr");
let data=[];

rows.forEach(r=>{
let c=r.querySelectorAll("td");

data.push({
Material:c[0].innerText,
Score:c[1].innerText,
Cost:c[2].innerText,
CO2:c[3].innerText
});
});

let ws = XLSX.utils.json_to_sheet(data);
let wb = XLSX.utils.book_new();

XLSX.utils.book_append_sheet(wb,ws,"Report");

XLSX.writeFile(wb,"report.xlsx");
}