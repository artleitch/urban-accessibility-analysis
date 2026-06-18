import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { LeafletModule } from '@asymmetrik/ngx-leaflet';
import { MapComponent } from './map/map';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, LeafletModule, MapComponent],
  templateUrl: './app.html',
  styleUrls: ['./app.scss']
})
export class App {
  protected readonly title = signal('accessibility-app');
}
