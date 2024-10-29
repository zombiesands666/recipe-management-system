class UnitConverter:
    # Conversion ratios for common recipe measurements
    CONVERSIONS = {
        # Volume conversions
        'ml_to_cups': 0.00422675,
        'ml_to_tbsp': 0.067628,
        'ml_to_tsp': 0.202884,
        'cups_to_ml': 236.588,
        'tbsp_to_ml': 14.7868,
        'tsp_to_ml': 4.92892,
        
        # Weight conversions
        'g_to_oz': 0.035274,
        'g_to_lb': 0.00220462,
        'oz_to_g': 28.3495,
        'lb_to_g': 453.592,
        
        # Temperature conversions
        'c_to_f': lambda c: (c * 9/5) + 32,
        'f_to_c': lambda f: (f - 32) * 5/9
    }
    
    @classmethod
    def convert(cls, value, from_unit, to_unit):
        """Convert between units"""
        if from_unit == to_unit:
            return value
            
        # Handle temperature conversions
        if from_unit.lower() == 'c' and to_unit.lower() == 'f':
            return cls.CONVERSIONS['c_to_f'](value)
        elif from_unit.lower() == 'f' and to_unit.lower() == 'c':
            return cls.CONVERSIONS['f_to_c'](value)
            
        # Handle other conversions
        conversion_key = f'{from_unit.lower()}_to_{to_unit.lower()}'
        if conversion_key in cls.CONVERSIONS:
            return value * cls.CONVERSIONS[conversion_key]
        
        # If direct conversion not found, try reverse
        reverse_key = f'{to_unit.lower()}_to_{from_unit.lower()}'
        if reverse_key in cls.CONVERSIONS:
            return value / cls.CONVERSIONS[reverse_key]
            
        raise ValueError(f"No conversion found for {from_unit} to {to_unit}")

    @classmethod
    def get_supported_units(cls):
        """Get lists of supported units"""
        volume_units = ['ml', 'cups', 'tbsp', 'tsp']
        weight_units = ['g', 'oz', 'lb']
        temp_units = ['C', 'F']
        
        return {
            'Volume': volume_units,
            'Weight': weight_units,
            'Temperature': temp_units
        }
