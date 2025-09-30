import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Button } from "./components/ui/button";
import { Badge } from "./components/ui/badge";
import { CheckCircle, ArrowRight, Home, Zap } from "lucide-react";
import { toast, Toaster } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Main Program Selection Page
const ProgramSelection = () => {
  const [programs, setPrograms] = useState([]);
  const [selectedProgram, setSelectedProgram] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPrograms();
  }, []);

  const fetchPrograms = async () => {
    try {
      const response = await axios.get(`${API}/programs`);
      setPrograms(response.data);
      setLoading(false);
    } catch (error) {
      toast.error("Failed to load programs");
      setLoading(false);
    }
  };

  const handleProgramSelect = async (program) => {
    setSelectedProgram(program);
    
    try {
      await axios.post(`${API}/select-program`, {
        program_id: program.id,
        program_name: program.name,
        user_session: `session_${Date.now()}`
      });
      
      toast.success(`Selected ${program.name} successfully!`);
      
      // Navigate to program details after a short delay
      setTimeout(() => {
        navigate(`/program/${program.id}`);
      }, 1000);
    } catch (error) {
      toast.error("Failed to select program");
      setSelectedProgram(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-emerald-600 mx-auto mb-4"></div>
          <p className="text-emerald-700 font-medium">Loading programs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-white/80 backdrop-blur-sm px-6 py-3 rounded-full shadow-lg mb-6">
            <Zap className="h-6 w-6 text-emerald-600" />
            <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
              Program Selection Hub
            </h1>
          </div>
          <p className="text-gray-600 text-lg max-w-2xl mx-auto">
            Choose from our collection of innovative programs. Select one to get started with your journey.
          </p>
        </div>

        {/* Programs Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 max-w-7xl mx-auto">
          {programs.map((program) => {
            const isSelected = selectedProgram?.id === program.id;
            const gradients = [
              'from-emerald-400 to-teal-500',
              'from-teal-400 to-cyan-500', 
              'from-cyan-400 to-blue-500',
              'from-blue-400 to-indigo-500',
              'from-indigo-400 to-violet-500',
              'from-violet-400 to-purple-500',
              'from-purple-400 to-pink-500',
              'from-pink-400 to-rose-500',
              'from-rose-400 to-orange-500',
              'from-orange-400 to-amber-500',
              'from-amber-400 to-yellow-500',
              'from-yellow-400 to-lime-500',
              'from-lime-400 to-green-500',
              'from-green-400 to-emerald-500',
              'from-red-400 to-pink-500'
            ];
            
            const programIndex = programs.findIndex(p => p.id === program.id);
            const gradientClass = gradients[programIndex % gradients.length];
            
            return (
              <Card 
                key={program.id} 
                className={`group cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-xl border-0 overflow-hidden ${
                  isSelected ? 'ring-4 ring-emerald-500 shadow-2xl scale-105' : 'shadow-lg hover:shadow-xl'
                }`}
                onClick={() => handleProgramSelect(program)}
              >
                <div className={`h-2 bg-gradient-to-r ${gradientClass}`}></div>
                
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-xl font-bold text-gray-800 group-hover:text-gray-900">
                      {program.name}
                    </CardTitle>
                    {isSelected && (
                      <CheckCircle className="h-6 w-6 text-emerald-500 animate-pulse" />
                    )}
                  </div>
                  <Badge 
                    variant="secondary" 
                    className={`w-fit bg-gradient-to-r ${gradientClass} text-white border-0 font-medium`}
                  >
                    {program.title}
                  </Badge>
                </CardHeader>
                
                <CardContent className="pt-0">
                  <CardDescription className="text-gray-600 leading-relaxed mb-4">
                    {program.description}
                  </CardDescription>
                  
                  <Button 
                    variant={isSelected ? "default" : "outline"}
                    className={`w-full group-hover:bg-gradient-to-r group-hover:${gradientClass} group-hover:text-white group-hover:border-0 transition-all duration-300 ${
                      isSelected ? `bg-gradient-to-r ${gradientClass} text-white border-0` : ''
                    }`}
                    disabled={isSelected}
                  >
                    {isSelected ? (
                      <>
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Selected
                      </>
                    ) : (
                      <>
                        Select Program
                        <ArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Footer */}
        <div className="text-center mt-16">
          <p className="text-gray-500 text-sm">
            Select a program to view detailed information and get started
          </p>
        </div>
      </div>
    </div>
  );
};

// Program Details Page
const ProgramDetails = () => {
  const { programId } = useParams();
  const [program, setProgram] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProgram();
  }, [programId]);

  const fetchProgram = async () => {
    try {
      const response = await axios.get(`${API}/programs/${programId}`);
      setProgram(response.data);
      setLoading(false);
    } catch (error) {
      toast.error("Failed to load program details");
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-emerald-600 mx-auto mb-4"></div>
          <p className="text-emerald-700 font-medium">Loading program details...</p>
        </div>
      </div>
    );
  }

  if (!program) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Program Not Found</h2>
          <Button onClick={() => navigate('/')} variant="outline">
            <Home className="h-4 w-4 mr-2" />
            Back to Programs
          </Button>
        </div>
      </div>
    );
  }

  const programIndex = parseInt(program.name.replace('Prg', '')) - 1;
  const gradients = [
    'from-emerald-400 to-teal-500',
    'from-teal-400 to-cyan-500', 
    'from-cyan-400 to-blue-500',
    'from-blue-400 to-indigo-500',
    'from-indigo-400 to-violet-500',
    'from-violet-400 to-purple-500',
    'from-purple-400 to-pink-500',
    'from-pink-400 to-rose-500',
    'from-rose-400 to-orange-500',
    'from-orange-400 to-amber-500',
    'from-amber-400 to-yellow-500',
    'from-yellow-400 to-lime-500',
    'from-lime-400 to-green-500',
    'from-green-400 to-emerald-500',
    'from-red-400 to-pink-500'
  ];
  const gradientClass = gradients[programIndex % gradients.length];

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Button 
            onClick={() => navigate('/')} 
            variant="outline" 
            className="mb-6 hover:bg-emerald-50"
          >
            <Home className="h-4 w-4 mr-2" />
            Back to Programs
          </Button>
          
          <div className="text-center">
            <div className={`inline-flex items-center gap-3 bg-gradient-to-r ${gradientClass} px-8 py-4 rounded-2xl shadow-lg mb-6 text-white`}>
              <Zap className="h-8 w-8" />
              <div>
                <h1 className="text-4xl font-bold">{program.name}</h1>
                <p className="text-lg opacity-90">{program.title}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Program Details */}
        <div className="max-w-4xl mx-auto">
          <Card className="shadow-2xl border-0 overflow-hidden">
            <div className={`h-4 bg-gradient-to-r ${gradientClass}`}></div>
            
            <CardHeader className="bg-white/80 backdrop-blur-sm">
              <CardTitle className="text-2xl text-gray-800 mb-2">Program Information</CardTitle>
              <CardDescription className="text-lg text-gray-600">
                Here are the details for the selected program
              </CardDescription>
            </CardHeader>
            
            <CardContent className="bg-white/50 backdrop-blur-sm p-8">
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-3">Description</h3>
                  <p className="text-gray-700 leading-relaxed text-lg">
                    {program.description}
                  </p>
                </div>
                
                <div className="grid md:grid-cols-2 gap-6 mt-8">
                  <div className="bg-white/70 rounded-xl p-6 shadow-sm">
                    <h4 className="font-semibold text-gray-800 mb-2">Program ID</h4>
                    <p className="text-gray-600 font-mono text-sm">{program.id}</p>
                  </div>
                  
                  <div className="bg-white/70 rounded-xl p-6 shadow-sm">
                    <h4 className="font-semibold text-gray-800 mb-2">Created</h4>
                    <p className="text-gray-600">{new Date(program.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
                
                <div className="text-center mt-8">
                  <div className={`inline-flex items-center gap-2 bg-gradient-to-r ${gradientClass} px-6 py-3 rounded-full text-white font-medium shadow-lg`}>
                    <CheckCircle className="h-5 w-5" />
                    Program Successfully Selected
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<ProgramSelection />} />
          <Route path="/program/:programId" element={<ProgramDetails />} />
        </Routes>
        <Toaster position="top-right" richColors />
      </BrowserRouter>
    </div>
  );
}

export default App;
