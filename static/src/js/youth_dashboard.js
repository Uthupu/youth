/** @odoo-module **/

import { Component, onWillStart, onMounted, onWillUnmount, useState, useRef } from "@odoo/owl";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

export class YouthNinjaDashboard extends Component {
    static template = "youth.NinjaDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.state = useState({
            data: {
                summary: {},
                breakdown: [],
                trend: { labels: [], income: [], expense: [] },
                recent_finances: [],
            },
            loading: true,
        });

        this.trendCanvasRef = useRef("trendCanvas");
        this.breakdownCanvasRef = useRef("breakdownCanvas");
        this.trendChart = null;
        this.breakdownChart = null;

        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            await this.loadDashboardData();
        });

        onMounted(() => {
            this.renderCharts();
        });

        onWillUnmount(() => {
            this.trendChart && this.trendChart.destroy();
            this.breakdownChart && this.breakdownChart.destroy();
        });
    }

    async loadDashboardData() {
        this.state.loading = true;
        const result = await this.orm.call("youth.event", "get_ninja_dashboard_data", []);
        this.state.data = result;
        this.state.loading = false;
        // Charts need to (re)render after the DOM updates with the new canvases
        setTimeout(() => this.renderCharts(), 0);
    }

    formatCurrency(value) {
        const n = Number(value) || 0;
        return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    renderCharts() {
        if (this.state.loading) {
            return;
        }
        this._renderTrendChart();
        this._renderBreakdownChart();
    }

    _renderTrendChart() {
        const canvas = this.trendCanvasRef.el;
        if (!canvas || typeof Chart === "undefined") {
            return;
        }
        const trend = this.state.data.trend || { labels: [], income: [], expense: [] };
        if (this.trendChart) {
            this.trendChart.destroy();
        }
        this.trendChart = new Chart(canvas.getContext("2d"), {
            type: "bar",
            data: {
                labels: trend.labels,
                datasets: [
                    {
                        label: "Income",
                        data: trend.income,
                        backgroundColor: "#2e9e6d",
                        borderRadius: 4,
                        maxBarThickness: 28,
                    },
                    {
                        label: "Expense",
                        data: trend.expense,
                        backgroundColor: "#d9534f",
                        borderRadius: 4,
                        maxBarThickness: 28,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom", labels: { boxWidth: 12, font: { size: 11 } } },
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { beginAtZero: true, grid: { color: "#eef0f3" } },
                },
            },
        });
    }

    _renderBreakdownChart() {
        const canvas = this.breakdownCanvasRef.el;
        if (!canvas || typeof Chart === "undefined") {
            return;
        }
        const breakdown = this.state.data.breakdown || [];
        if (this.breakdownChart) {
            this.breakdownChart.destroy();
        }
        const palette = ["#3b6ef6", "#f0ad4e", "#5bc0de", "#8e6fce", "#8a94a6"];
        this.breakdownChart = new Chart(canvas.getContext("2d"), {
            type: "doughnut",
            data: {
                labels: breakdown.map((b) => b.label),
                datasets: [
                    {
                        data: breakdown.map((b) => Math.max(b.profit, 0)),
                        backgroundColor: palette,
                        borderWidth: 2,
                        borderColor: "#ffffff",
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "62%",
                plugins: {
                    legend: { position: "bottom", labels: { boxWidth: 12, font: { size: 11 } } },
                },
            },
        });
    }

    openEventView(eventType = null) {
        let domain = [];
        let name = 'Activities';
        if (eventType) {
            domain = [['event_type', '=', eventType]];
        }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: name,
            res_model: 'youth.event',
            views: [[false, 'list'], [false, 'form']],
            domain: domain,
        });
    }

    showIncomeInfo() {
        this.env.services.dialog.add(AlertDialog, {
            title: "💰 Total Income",
            body: `The total income recorded is ₹${this.formatCurrency(this.state.data.summary.total_income)}.`,
        });
    }

    showExpenseInfo() {
        this.env.services.dialog.add(AlertDialog, {
            title: "💸 Total Expense",
            body: `The total expense recorded is ₹${this.formatCurrency(this.state.data.summary.total_expense)}.`,
        });
    }
}

registry.category("actions").add("youth_ninja_dashboard_tag", YouthNinjaDashboard);
