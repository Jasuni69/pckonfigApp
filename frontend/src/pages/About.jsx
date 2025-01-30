const About = () => {
  return (
    <div className="wrapper bg-gradient-to-b from-slate-300 to-slate-200">
      <div className="min-h-screen flex flex-col items-center justify-center px-4">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">PCkonfig</h1>
        <p className="text-lg text-gray-600 text-center max-w-2xl mb-6">
          Välkommen till PCkonfig.se - din guide till att bygga din egen dator. Vårt mål är att göra PC-byggande enkelt och tillgängligt för alla, oavsett erfarenhetsnivå.
        </p>
        <div className="text-lg text-gray-600 max-w-2xl">
          <p className="mb-2">Med vårt verktyg kan du:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li>Skapa en anpassad dator för dina behov</li>
            <li>Kontrollera kompatibilitet mellan komponenter</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default About;