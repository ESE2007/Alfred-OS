package com.tonada.mobile

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Computer
import androidx.compose.material.icons.filled.PhoneAndroid
import androidx.compose.material.icons.filled.QrCodeScanner
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.journeyapps.barcodescanner.ScanContract
import com.journeyapps.barcodescanner.ScanOptions
import com.tonada.mobile.core.MqttClient
import com.tonada.mobile.core.PairInfo

private fun linkPc(text: String): Boolean {
    val p = PairInfo.parse(text)
    if (p == null) {
        Model.msg("Ese código no es de Tonada")
        return false
    }
    Model.setPair(p)
    Model.msg("Vinculado con " + p.name)
    return true
}

@Composable
private fun DeviceCard(selected: Boolean, title: String, subtitle: String, pc: Boolean, onClick: () -> Unit) {
    val c = MaterialTheme.colorScheme
    Row(
        Modifier.fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(if (selected) c.secondaryContainer else c.surfaceVariant)
            .clickable { onClick() }
            .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            if (pc) Icons.Filled.Computer else Icons.Filled.PhoneAndroid, contentDescription = null,
            tint = if (selected) c.primary else c.onSurfaceVariant,
        )
        Spacer(Modifier.width(14.dp))
        Column(Modifier.weight(1f)) {
            Text(title, fontWeight = FontWeight.Medium)
            Text(subtitle, style = MaterialTheme.typography.bodySmall, color = c.onSurfaceVariant)
        }
        if (selected) Icon(Icons.Filled.Check, contentDescription = "Activo", tint = c.primary)
    }
}

@Composable
fun DevicesScreen() {
    val pair = Model.pair
    var pasted by remember { mutableStateOf("") }
    var confirmUnlink by remember { mutableStateOf(false) }
    var name by remember { mutableStateOf(Model.prefs.deviceName) }
    val dim = MaterialTheme.colorScheme.onSurfaceVariant

    val scan = rememberLauncherForActivityResult(ScanContract()) { r ->
        val txt = r.contents
        if (txt != null) linkPc(txt)
    }

    val pcStatus = when {
        pair == null -> ""
        Model.rStatus == MqttClient.Status.ONLINE && Model.rState?.off == true -> "Tonada está cerrado en el PC"
        Model.rStatus == MqttClient.Status.ONLINE && Model.rState == null -> "Conectado, esperando al PC…"
        Model.rStatus == MqttClient.Status.ONLINE -> "En línea"
        Model.rStatus == MqttClient.Status.CONNECTING -> "Conectando…"
        else -> "Sin conexión" + (Model.rDetail?.let { " ($it)" } ?: "")
    }

    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
    ) {
        Text("Reproducir en", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(10.dp))
        DeviceCard(!Model.controlPc, "Este teléfono", "Música guardada aquí", false) { Model.setActive(false) }
        if (pair != null) {
            Spacer(Modifier.height(8.dp))
            DeviceCard(Model.controlPc, pair.name, pcStatus, true) {
                Model.setActive(true)
            }
            Spacer(Modifier.height(16.dp))
            Button(
                onClick = { Model.transferToPc() },
                enabled = Model.pcReachable,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("Seguir en el PC lo que suena aquí") }
            Spacer(Modifier.height(8.dp))
            OutlinedButton(
                onClick = { Model.transferToPhone() },
                enabled = Model.pcReachable,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("Traer al teléfono lo que suena en el PC") }
            Spacer(Modifier.height(6.dp))
            Text(
                "Las canciones se reconocen por nombre de archivo y tamaño (o por título y artista), así que las dos " +
                    "bibliotecas deben tener los mismos archivos.",
                style = MaterialTheme.typography.bodySmall, color = dim,
            )
        }

        Spacer(Modifier.height(28.dp))
        Text(if (pair == null) "Vincular con el PC" else "Vinculación", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(8.dp))
        if (pair == null) {
            Text(
                "En Tonada para PC abre Ajustes → Control remoto móvil, activa «Activar control remoto móvil» y pulsa «Mostrar código QR…». " +
                    "Luego escanea el código QR que aparece. Funciona por internet: no hace falta estar en la misma red.",
                style = MaterialTheme.typography.bodyMedium, color = dim,
            )
            Spacer(Modifier.height(12.dp))
            Button(
                onClick = {
                    scan.launch(
                        ScanOptions()
                            .setDesiredBarcodeFormats(ScanOptions.QR_CODE)
                            .setPrompt("Apunta al código QR de Tonada en el PC")
                            .setBeepEnabled(false)
                    )
                },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Icon(Icons.Filled.QrCodeScanner, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(Modifier.width(8.dp))
                Text("Escanear código QR")
            }
            Spacer(Modifier.height(12.dp))
            OutlinedTextField(
                value = pasted,
                onValueChange = { pasted = it },
                label = { Text("…o pega aquí el código (tonada://pair?…)") },
                modifier = Modifier.fillMaxWidth(),
                maxLines = 3,
            )
            Spacer(Modifier.height(8.dp))
            OutlinedButton(
                onClick = { if (linkPc(pasted)) pasted = "" },
                enabled = pasted.isNotBlank(),
                modifier = Modifier.fillMaxWidth(),
            ) { Text("Vincular con el código") }
        } else {
            Text(
                "Vinculado con «${pair.name}». La conexión va cifrada de extremo a extremo; el relé público solo ve " +
                    "mensajes ilegibles.",
                style = MaterialTheme.typography.bodyMedium, color = dim,
            )
            Spacer(Modifier.height(4.dp))
            Text("Relé: " + pair.broker, style = MaterialTheme.typography.bodySmall, color = dim)
            Spacer(Modifier.height(12.dp))
            OutlinedButton(onClick = { confirmUnlink = true }, modifier = Modifier.fillMaxWidth()) { Text("Desvincular") }
        }

        Spacer(Modifier.height(28.dp))
        Text("Este teléfono", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(8.dp))
        OutlinedTextField(
            value = name,
            onValueChange = { name = it },
            label = { Text("Nombre que verá el PC") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
        )
        Spacer(Modifier.height(8.dp))
        OutlinedButton(
            onClick = {
                Model.setDeviceName(name)
                name = Model.prefs.deviceName
                Model.msg("Nombre guardado")
            },
            modifier = Modifier.fillMaxWidth(),
        ) { Text("Guardar nombre") }
        Spacer(Modifier.height(24.dp))
    }

    if (confirmUnlink) {
        AlertDialog(
            onDismissRequest = { confirmUnlink = false },
            title = { Text("¿Desvincular?") },
            text = { Text("Dejarás de poder controlar este PC hasta que lo vincules otra vez con su código QR.") },
            confirmButton = {
                TextButton(onClick = {
                    confirmUnlink = false
                    Model.setPair(null)
                }) { Text("Desvincular") }
            },
            dismissButton = { TextButton(onClick = { confirmUnlink = false }) { Text("Cancelar") } },
        )
    }
}
