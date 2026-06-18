import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { THRESHOLD_OPTIONS, ThresholdOption } from './threshold-selector.constants';
import { parseThresholdValue } from '../utils/component-utils';

@Component({
  selector: 'threshold-selector',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './threshold-selector.html',
  styleUrls: ['./threshold-selector.scss']
})
export class ThresholdSelectorComponent {
  @Input() selectedValue = 15;
  @Output() selectionChange = new EventEmitter<number>();

  protected readonly thresholds: ThresholdOption[] = THRESHOLD_OPTIONS;

  protected onSelectChange(value: string): void {
    this.selectionChange.emit(parseThresholdValue(value));
  }
}
