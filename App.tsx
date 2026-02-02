import React, { useState, useCallback } from 'react';
import { MessageSquare, Utensils, Zap, Plus, Trash2, Smartphone, Save, RefreshCw, AlertCircle } from 'lucide-react';
import { generateWhatsAppCopy } from '../services/gemini';
import { RestaurantConfig, MenuItem, GeneratedMessages } from '../types';
import { WhatsAppPreview } from './WhatsAppPreview';

// Default initial state
const INITIAL_MENU: MenuItem[] = [
  { id: '1', name: 'Cheesy Smash Burger', price: '$12' },
  { id: '2', name: 'Pepperoni Pizza XL', price: '$18' },
  { id: '3', name: 'Truffle Fries', price: '$8' },
];

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'config' | 'preview'>('config');
  
  const [config, setConfig] = useState<RestaurantConfig>({
    name: "Burger & Bites",
    cuisine: "American Fast Food",
    upiId: "9876543210@upi",
    menuItems: INITIAL_MENU,
    tone: 'fun',
  });

  const [generatedMessages, setGeneratedMessages] = useState<GeneratedMessages | null>(null);

  const handleAddItem = () => {
    setConfig(prev => ({
      ...prev,
      menuItems: [...prev.menuItems, { id: Date.now().toString(), name: '', price: '' }]
    }));
  };

  const handleRemoveItem = (id: string) => {
    setConfig(prev => ({
      ...prev,
      menuItems: prev.menuItems.filter(item => item.id !== id)
    }));
  };

  const handleItemChange = (id: string, field: keyof MenuItem, value: string) => {
    setConfig(prev => ({
      ...prev,
      menuItems: prev.menuItems.map(item => 
        item.id === id ? { ...item, [field]: value } : item
      )
    }));
  };

  const handleGenerate = async () => {
    if (!process.env.API_KEY) {
        setError("API Key is missing. Please check your environment configuration.");
        return;
    }
    
    setLoading(true);
    setError(null);
    try {
      const messages = await generateWhatsAppCopy(config);
      setGeneratedMessages(messages);
      setActiveTab('preview');
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate content. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col md:flex-row">
      
      {/* Left Panel - Configuration */}
      <div className={`w-full md:w-1/2 p-6 overflow-y-auto h-screen transition-all duration-300 ${activeTab === 'preview' ? 'hidden md:block' : 'block'}`}>
        <div className="max-w-xl mx-auto">
          <header className="mb-8">
            <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
              <span className="bg-green-500 text-white p-2 rounded-lg"><MessageSquare size={24} /></span>
              WhatsApp Chef
            </h1>
            <p className="text-slate-500 mt-2">
              Generate perfect, emoji-rich scripts for your manual ordering system.
            </p>
          </header>

          <div className="space-y-6 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            
            {/* Restaurant Info */}
            <section className="space-y-4">
              <h2 className="text-lg font-semibold text-slate-700 flex items-center gap-2">
                <Utensils size={18} /> Restaurant Details
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-600 mb-1">Business Name</label>
                  <input 
                    type="text" 
                    value={config.name}
                    onChange={(e) => setConfig({...config, name: e.target.value})}
                    className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                    placeholder="e.g. Joe's Burgers"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-600 mb-1">Cuisine / Vibe</label>
                  <input 
                    type="text" 
                    value={config.cuisine}
                    onChange={(e) => setConfig({...config, cuisine: e.target.value})}
                    className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                    placeholder="e.g. Italian, Street Food"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1">Payment UPI / Link</label>
                <input 
                  type="text" 
                  value={config.upiId}
                  onChange={(e) => setConfig({...config, upiId: e.target.value})}
                  className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                  placeholder="e.g. 9876543210@upi"
                />
              </div>
            </section>

            {/* Menu Items */}
            <section className="space-y-4 pt-4 border-t border-slate-100">
               <div className="flex justify-between items-center">
                <h2 className="text-lg font-semibold text-slate-700">Popular Menu Items</h2>
                <button 
                  onClick={handleAddItem}
                  className="text-sm text-green-600 font-medium hover:text-green-700 flex items-center gap-1"
                >
                  <Plus size={16} /> Add Item
                </button>
               </div>
               
               <div className="space-y-3">
                 {config.menuItems.map((item) => (
                   <div key={item.id} className="flex gap-2 items-center">
                     <input 
                        type="text" 
                        value={item.name}
                        onChange={(e) => handleItemChange(item.id, 'name', e.target.value)}
                        placeholder="Item Name"
                        className="flex-1 p-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-green-500 outline-none"
                     />
                     <input 
                        type="text" 
                        value={item.price}
                        onChange={(e) => handleItemChange(item.id, 'price', e.target.value)}
                        placeholder="Price"
                        className="w-20 p-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-green-500 outline-none"
                     />
                     <button 
                      onClick={() => handleRemoveItem(item.id)}
                      className="text-slate-400 hover:text-red-500 p-1"
                    >
                       <Trash2 size={16} />
                     </button>
                   </div>
                 ))}
               </div>
            </section>

            {/* Actions */}
            <div className="pt-6">
              <button 
                onClick={handleGenerate}
                disabled={loading}
                className="w-full bg-slate-900 text-white py-3 rounded-xl font-semibold shadow-lg hover:bg-slate-800 transition-all transform active:scale-95 flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <RefreshCw className="animate-spin" size={20} /> Generating Magic...
                  </>
                ) : (
                  <>
                    <Zap size={20} /> Generate WhatsApp Copy
                  </>
                )}
              </button>
              {error && (
                <div className="mt-4 p-3 bg-red-50 text-red-700 text-sm rounded-lg flex items-center gap-2">
                  <AlertCircle size={16} /> {error}
                </div>
              )}
            </div>

          </div>
          
          <div className="mt-8 p-4 bg-blue-50 border border-blue-100 rounded-xl text-sm text-blue-800">
            <strong>Pro Tip for Developers:</strong> Use these generated strings in your GitHub/Streamlit/Twilio setup. Store them as string templates in your Python backend to automate responses.
          </div>
        </div>
      </div>

      {/* Right Panel - Preview (Mobile Tabs logic handled by visibility classes) */}
      <div className={`w-full md:w-1/2 bg-[#e5ddd5] relative flex flex-col h-screen ${activeTab === 'config' ? 'hidden md:flex' : 'flex'}`}>
        
        {/* Mobile Header */}
        <div className="md:hidden bg-slate-800 text-white p-4 flex items-center gap-3">
          <button onClick={() => setActiveTab('config')} className="text-slate-300 hover:text-white">Back</button>
          <span className="font-semibold">Preview</span>
        </div>

        {/* Wallpaper Pattern Overlay */}
        <div className="absolute inset-0 opacity-10 pointer-events-none" 
             style={{ backgroundImage: `url("https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png")` }}>
        </div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 relative z-10">
          {!generatedMessages ? (
             <div className="h-full flex flex-col items-center justify-center text-gray-500 opacity-60">
                <Smartphone size={64} className="mb-4" />
                <p className="text-center max-w-xs">Enter your menu details on the left and hit generate to see your WhatsApp bot preview here.</p>
             </div>
          ) : (
            <div className="max-w-md mx-auto space-y-8">
              
              <div className="text-center my-4">
                <span className="bg-[#dcf8c6] text-gray-600 px-3 py-1 rounded-full text-xs shadow-sm uppercase font-bold tracking-widest">
                  Preview Mode
                </span>
              </div>

              {/* Message 1: Welcome */}
              <WhatsAppPreview 
                title="1. Welcome & Menu (Auto-reply)" 
                text={generatedMessages.welcomeMessage} 
                isSent={false}
                onCopy={copyToClipboard}
              />

              {/* Message 2: Bill */}
              <WhatsAppPreview 
                title="2. Bill Template (Manual Send)" 
                text={generatedMessages.billTemplate} 
                isSent={false}
                onCopy={copyToClipboard}
              />

              {/* Message 3: Kitchen */}
              <WhatsAppPreview 
                title="3. Confirmation (Auto-reply)" 
                text={generatedMessages.kitchenMessage} 
                isSent={false}
                onCopy={copyToClipboard}
              />
              
              <div className="flex justify-center pb-10">
                 <button 
                  onClick={() => alert("Ready for your Python/Twilio script!")}
                  className="bg-white text-green-600 px-6 py-2 rounded-full font-semibold shadow-md flex items-center gap-2 hover:bg-gray-50 transition"
                 >
                   <Save size={18} /> Export All JSON
                 </button>
              </div>
            </div>
          )}
        </div>
      </div>

    </div>
  );
}
