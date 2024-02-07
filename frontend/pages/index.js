import React, { useState, useEffect } from 'react';

function Home() {
    const [message, setMessage] = useState('');

    useEffect(() => {
        async function fetchData() {
            const response = await fetch('http://localhost:5000/');
            const data = await response.text();
            setMessage(data);
        }
        fetchData();
    }, []);

    return (
        <div>
            <h1>Hello</h1>
            <p>Message from Flask server:</p>
            <p>{message}</p>
        </div>
    );
}

export default Home;
