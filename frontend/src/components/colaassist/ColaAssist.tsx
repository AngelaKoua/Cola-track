"use client";

import React, { useState, useRef, useEffect } from "react";
import {
    X,
    Sparkles,
    Send
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";

// ─── Types ───────────────────────────────────────────────────
type ChatMessageRole = "user" | "model";
type ChatMessageItem = {
    role: ChatMessageRole;
    content: string;
    faqAnswer?: {
        explanation: string;
        interpretation?: string | null;
        actions?: string[];
    };
};

export default function ColaAssist() {
    const { user } = useAuth();
    const [open, setOpen] = useState(false);
    const popupRef = useRef<HTMLDivElement>(null);
    const chatEndRef = useRef<HTMLDivElement>(null);

    // Chat state
    const initialMessage: ChatMessageItem = {
        role: "model",
        content: "Bonjour, je suis ColaAssist. Posez-moi votre question sur la plateforme ou sur les données industrielles."
    };
    
    const [history, setHistory] = useState<ChatMessageItem[]>([initialMessage]);
    const [isLoading, setIsLoading] = useState(false);
    const [inputValue, setInputValue] = useState("");

    // Close popup when clicking outside
    useEffect(() => {
        function handler(e: MouseEvent) {
            if (popupRef.current && !popupRef.current.contains(e.target as Node)) {
                setOpen(false);
            }
        }
        if (open) document.addEventListener("mousedown", handler);
        return () => document.removeEventListener("mousedown", handler);
    }, [open]);

    // Auto-scroll chat
    useEffect(() => {
        if (open && chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [open, history, isLoading]);

    const toggle = () => {
        setOpen((o) => !o);
    };

    // ─── Chat Logic ──────────────────────────────────────────
    const getContext = () => {
        const page = typeof window !== 'undefined' ? window.location.pathname : "";
        const machine = document.getElementById("cola-context-machine")?.getAttribute("data-machine") || undefined;
        const indicators = document.getElementById("cola-context-indicators")?.getAttribute("data-indicators") || undefined;
        return { page, machine, indicators };
    };

    const handleSendMessage = async (e?: React.FormEvent) => {
        if (e) e.preventDefault();
        if (!inputValue.trim() || isLoading) return;

        const userMsg: ChatMessageItem = { role: "user", content: inputValue.trim() };
        
        setHistory(prev => [...prev, userMsg]);
        setInputValue("");
        setIsLoading(true);

        try {
            const apiMessages = [...history, userMsg]
                .filter(m => m.role === "user" || m.role === "model")
                .map(m => ({ role: m.role, content: m.content }));
                
            const contextPayload = getContext();
            
            const response = await fetch("http://localhost:8000/api/ai/chat/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ messages: apiMessages, context: contextPayload })
            });
            
            if (!response.ok) throw new Error("API Error");
            
            const data = await response.json();
            const aiMsg: ChatMessageItem = {
                role: "model",
                content: data.explanation, 
                faqAnswer: {
                    explanation: data.explanation,
                    interpretation: data.interpretation,
                    actions: data.actions
                }
            };
            
            setHistory(prev => [...prev, aiMsg]);
        } catch (error) {
            console.error(error);
            const errorMsg: ChatMessageItem = {
                role: "model",
                content: "Erreur",
                faqAnswer: {
                    explanation: "Désolé, une erreur s'est produite lors de la connexion à l'IA.",
                }
            };
            setHistory(prev => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    // ─── Render views ────────────────────────────────────────
    const renderChat = () => {
        return (
            <div className="cola-body cola-chat-wrapper">
                <div className="cola-chat-messages">
                    {history.map((msg, idx) => (
                        <div key={idx} className={`cola-chat-msg ${msg.role === 'user' ? 'cola-msg-user' : 'cola-msg-ai'}`}>
                            {msg.role === 'user' ? (
                                <p className="cola-msg-text">{msg.content}</p>
                            ) : (
                                <div className="cola-msg-structured cola-answer-body">
                                    {(msg.faqAnswer?.explanation || msg.content) && (
                                        <div className="cola-answer-section">
                                            <p className="cola-answer-text">{msg.faqAnswer?.explanation || msg.content}</p>
                                        </div>
                                    )}
                                    {msg.faqAnswer?.interpretation && (
                                        <div className="cola-answer-section">
                                            <h4 className="cola-answer-heading">Comment l'interpréter</h4>
                                            <p className="cola-answer-text">{msg.faqAnswer.interpretation}</p>
                                        </div>
                                    )}
                                    {msg.faqAnswer?.actions && msg.faqAnswer.actions.length > 0 && (
                                        <div className="cola-answer-section">
                                            <h4 className="cola-answer-heading">Actions recommandées</h4>
                                            <ol className="cola-steps">
                                                {msg.faqAnswer.actions.map((s, i) => (
                                                    <li key={i} className="cola-step">
                                                        <span className="cola-step-num">{i + 1}</span>
                                                        <span>{s}</span>
                                                    </li>
                                                ))}
                                            </ol>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                    {isLoading && (
                        <div className="cola-chat-msg cola-msg-ai">
                            <div className="cola-typing-indicator">
                                <span></span><span></span><span></span>
                            </div>
                        </div>
                    )}
                    <div ref={chatEndRef} style={{ height: 1 }} />
                </div>
                
                <form className="cola-chat-input-form" onSubmit={handleSendMessage}>
                    <input 
                        type="text" 
                        className="cola-chat-input" 
                        placeholder="Posez votre question..." 
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        disabled={isLoading}
                    />
                    <button type="submit" className="cola-chat-send-btn" disabled={!inputValue.trim() || isLoading}>
                        <Send size={16} />
                    </button>
                </form>
            </div>
        );
    };

    return (
        <>
            {/* ─── Floating Action Button ────────────────────── */}
            <button
                className={`cola-fab ${open ? "cola-fab--open" : ""}`}
                onClick={toggle}
                aria-label="Ouvrir ColaAssist"
                id="colaassist-fab"
            >
                {open ? <X size={24} /> : <Sparkles size={24} />}
            </button>

            {/* ─── Popup ─────────────────────────────────────── */}
            {open && (
                <div className="cola-popup" ref={popupRef}>
                    {/* Header */}
                    <div className="cola-header">
                        <span className="cola-header-title">ColaAssist</span>
                        <button className="cola-close" onClick={() => setOpen(false)} aria-label="Fermer">
                            <X size={18} />
                        </button>
                    </div>

                    {/* Body */}
                    {renderChat()}
                </div>
            )}
        </>
    );
}
