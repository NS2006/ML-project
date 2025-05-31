tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: '#6c5ce7',
                secondary: '#a29bfe',
                accent: '#fd79a8',
                dark: '#2d3436',
                light: '#f5f6fa',
                text: '#636e72',
            },
            fontFamily: {
                poppins: ['Poppins', 'sans-serif'],
            },
            animation: {
                float: 'float 6s ease-in-out infinite',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-20px)' },
                }
            }
        }
    }
}