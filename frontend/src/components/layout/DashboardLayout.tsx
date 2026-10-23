import { Sidebar } from "./Sidebar"
import { Header } from "./Header"
import ColaAssist from "@/components/colaassist/ColaAssist"
import "@/components/colaassist/colaassist.css"

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <div className="flex h-screen bg-background overflow-hidden">
            <Sidebar />
            <div className="flex-1 flex flex-col overflow-hidden">
                <Header />
                <main className="flex-1 overflow-y-auto p-6">
                    {children}
                </main>
            </div>
            <ColaAssist />
        </div>
    )
}
