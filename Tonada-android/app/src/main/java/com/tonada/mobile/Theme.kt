package com.tonada.mobile

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val TonadaColors = darkColorScheme(
    primary = Color(0xFF6C7BFF),
    onPrimary = Color.White,
    background = Color(0xFF0F1115),
    onBackground = Color(0xFFECEEF4),
    surface = Color(0xFF161922),
    onSurface = Color(0xFFECEEF4),
    surfaceVariant = Color(0xFF1D212C),
    onSurfaceVariant = Color(0xFF9AA1B2),
    secondaryContainer = Color(0xFF2A3052),
    onSecondaryContainer = Color(0xFFECEEF4),
    error = Color(0xFFFF5D6C),
    outline = Color(0xFF6C7385),
)

@Composable
fun TonadaTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = TonadaColors, content = content)
}
