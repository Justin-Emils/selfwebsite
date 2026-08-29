import React ,{useState,useEffect}from "react";
import Loading from "./components/Loading";
function App() {
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);}, []);

  if (loading) {
      return (<Loading />);
  }
    
  return (
    <div className="App">
    </div>
  );

}

export default App;